import os
from api import logger
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_talisman import Talisman
from pydantic import ValidationError
import threading
from werkzeug.middleware.proxy_fix import ProxyFix

from .service import start_agent, get_session, interrupt_session, read_session_state
from .model import FactCheckRequest

app = Flask(__name__)

# 配置代理信息，用于生产环境中的反向代理
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)

# 安全配置
# 在生产环境中限制CORS
if os.getenv('FLASK_ENV') == 'production':
    print("production")
    allowed_origins = os.getenv('ALLOWED_ORIGINS', '*').split(',')
    print(f"Allowed origins: {allowed_origins}")
    CORS(app, 
         resources={r"/api/*": {"origins": allowed_origins}},
         supports_credentials=True,
         allow_headers=["Content-Type", "Authorization"],
         methods=["GET", "POST", "OPTIONS"])
else:
    print("development")
    CORS(app)  # 开发环境允许所有来源

# 配置内容安全策略
csp = {
    'default-src': "'self'",
    'script-src': ["'self'", "'unsafe-inline'"],
    'style-src': ["'self'", "'unsafe-inline'"],
    'img-src': ["'self'", 'data:'],
    'connect-src': ["'self'", '*']  # 允许API连接
}

# 启用安全头
Talisman(app, 
         content_security_policy=csp,
         content_security_policy_nonce_in=['script-src'],
         force_https=os.getenv('FLASK_ENV') == 'production',
         strict_transport_security=True,
         strict_transport_security_preload=True,
         session_cookie_secure=os.getenv('FLASK_ENV') == 'production',
         session_cookie_http_only=True,
         feature_policy={
             'geolocation': "'none'",
             'microphone': "'none'",
             'camera': "'none'"
         })

app.config['PREFERRED_URL_SCHEME'] = 'https'

# 跟踪活跃的SSE连接
active_connections = {}
connection_lock = threading.Lock()

@app.route('/api/start-fact-check', methods=['POST'])
def create_and_run_agent():
    """创建一个新的 agent 实例并立即开始核查"""
    try:
        # 验证请求数据
        data = request.json
        if not data:
            return jsonify({"error": "Missing request data"}), 400
        
        # 使用 Pydantic 模型验证请求
        fact_check_request = FactCheckRequest(**data)
        
        # 启动 Agent 并获取会话 ID
        session_id = start_agent(
            fact_check_request.news_text,
            fact_check_request.config
        )
        
        # 返回会话 ID 给客户端
        return jsonify({
            "session_id": session_id,
            "message": "核查已开始"
        })
    
    except ValidationError as e:
        # 处理验证错误
        logger.error(f"验证错误: {e}")
        return jsonify({"error": str(e)}), 400
    
    except Exception as e:
        # 处理其他错误
        logger.error(f"启动核查错误: {e}")
        return jsonify({"error": f"启动核查失败: {str(e)}"}), 500

@app.route('/api/agents/<session_id>/events', methods=['GET'])
def get_agent_events(session_id):
    """
    SSE 接口，返回 agent 执行过程中的事件流
    前端可以通过 EventSource 订阅这个接口接收实时事件
    """
    # 检查会话是否存在
    session = get_session(session_id)
    if not session:
        # 检查文件系统中是否存在会话
        file_state = read_session_state(session_id)
        if file_state and file_state.get("is_running", False):
            logger.warning(f"会话 ID '{session_id}' 在内存中不存在，但在文件系统中找到 - 可能在其他 worker 中运行")
            return jsonify({"error": f"会话 ID '{session_id}' 在当前进程中不可用，请重新连接或刷新页面"}), 409
        return jsonify({"error": f"会话 ID '{session_id}' 不存在"}), 404
    
    # 如果会话存在但在其他 worker 中
    if session.get("exists_in_other_worker", False):
        logger.warning(f"会话 ID '{session_id}' 在其他 worker 中运行，无法在当前进程中访问")
        return jsonify({"error": f"会话 ID '{session_id}' 在当前进程中不可用，请重新连接或刷新页面"}), 409
    
    # 获取 SSE 会话
    sse_session = session["sse_session"]
    logger.info(f"Client connected to SSE stream for session: {session_id}")
    
    # 使用 SSE 会话的 get_response 方法获取响应
    response = sse_session.get_response()
    
    # 注册一个关闭回调函数，在客户端断开连接时调用
    @response.call_on_close
    def on_close():
        logger.info(f"Client disconnected from SSE stream for session: {session_id}")
        # 中断会话并清理资源
        interrupt_session(session_id)
    
    return response

@app.route('/api/agents/<session_id>/interrupt', methods=['POST'])
def interrupt_agent(session_id):
    """中断正在运行的 agent 任务"""
    logger.info(f"收到中断请求: session_id={session_id}")
    
    # 检查会话是否存在
    session = get_session(session_id)
    if not session:
        logger.warning(f"中断请求失败: 会话 ID '{session_id}' 不存在")
        return jsonify({"error": f"会话 ID '{session_id}' 不存在或无法中断"}), 404
        
    try:
        # 尝试中断会话
        result = interrupt_session(session_id)
        if not result:
            logger.warning(f"中断请求处理失败: 会话 ID '{session_id}' 无法中断")
            return jsonify({"error": f"会话 ID '{session_id}' 不存在或无法中断"}), 404
        
        logger.info(f"会话 '{session_id}' 已成功中断")
        return jsonify({
            "message": f"会话 '{session_id}' 已成功中断"
        })
    except Exception as e:
        # 捕获所有异常以确保请求总是得到响应
        logger.error(f"中断请求处理异常: {e}")
        return jsonify({"error": f"中断请求处理异常: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', '8000'))
    app.run(
        debug=os.getenv('FLASK_ENV') == 'development', 
        host='0.0.0.0', 
        port=port, 
        threaded=True
    )
