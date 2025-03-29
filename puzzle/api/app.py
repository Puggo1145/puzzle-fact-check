from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import json
import time
import traceback
import logging
import threading
from pydantic import ValidationError

from .service import agent_service
from .model import FactCheckRequest

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('puzzle_api')

app = Flask(__name__)
CORS(app)  # 启用 CORS 以支持前端跨域调用

# 跟踪活跃的SSE连接
active_connections = {}
connection_lock = threading.Lock()

@app.route('/api/start-fact-check', methods=['POST'])
def create_and_run_agent():
    """创建一个新的 agent 实例并立即开始核查"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        try:
            fact_check_request = FactCheckRequest(**data)
        except ValidationError as e:
            logger.error(f"Validation error: {str(e)}")
            return jsonify({"errors": e.errors()}), 400
        
        news_text = fact_check_request.news_text
        config = fact_check_request.config
        
        logger.info(f"Creating agent with config: {config}")
        session_id = agent_service.create_agent(config)
        logger.info(f"Agent created with session_id: {session_id}")
        
        logger.info(f"Running agent {session_id} with news_text: {news_text[:50]}...")
        agent_service.run_agent(session_id, news_text)
        
        return jsonify({"status": "running", "session_id": session_id})
    except Exception as e:
        logger.error(f"Error in create_and_run_agent: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/agents/<session_id>/events', methods=['GET'])
def get_agent_events(session_id):
    """
    SSE 接口，返回 agent 执行过程中的事件流
    前端可以通过 EventSource 订阅这个接口接收实时事件
    """
    logger.info(f"Client connected to SSE stream for session {session_id}")
    
    # 检查session是否存在
    if session_id not in agent_service.agent_instances:
        logger.error(f"Session {session_id} not found")
        return jsonify({"error": "Session not found"}), 404
    
    # 注册这个连接
    client_id = f"{session_id}_{threading.get_ident()}"
    with connection_lock:
        active_connections[client_id] = session_id
    
    def generate():
        event_count = 0
        task_completed = False
        connection_closed = False
        
        try:
            while True:
                # 如果连接关闭，立即退出
                if connection_closed:
                    logger.info(f"Connection marked as closed for {client_id}, stopping stream")
                    break
                
                # 如果任务已经完成，停止生成事件和心跳
                if task_completed:
                    logger.info(f"Task completed for session {session_id}, stopping event stream")
                    break
                    
                # 定期检查连接状态
                if client_id not in active_connections:
                    logger.info(f"Connection {client_id} was marked as closed, stopping stream")
                    break
                
                # 获取队列中的事件，如果没有则等待一段时间
                event = agent_service.get_events(session_id)
                if event:
                    event_count += 1
                    event_type = event["event"]
                    logger.info(f"Sending event {event_count} of type {event_type} for session {session_id}")
                    
                    # 检查是否为任务完成或中断事件
                    if event_type in ["task_complete", "task_interrupted"]:
                        task_completed = True
                        # 清理资源但保留会话
                        agent_service.cleanup_resources(session_id)
                    
                    # 确保数据可以被JSON序列化
                    try:
                        data = json.dumps(event["data"])
                        yield f"event: {event_type}\ndata: {data}\n\n"
                        
                        # 如果是任务完成/中断事件，在发送后立即停止
                        if task_completed:
                            # 给前端一点时间处理最后的事件
                            time.sleep(0.5)
                            break
                    except TypeError as e:
                        logger.error(f"JSON serialization error for event {event_type} in session {session_id}: {str(e)}")
                        error_data = json.dumps({"error": f"序列化错误: {str(e)}"})
                        yield f"event: error\ndata: {error_data}\n\n"
                    except Exception as e:
                        logger.error(f"Unexpected error processing event {event_type} in session {session_id}: {str(e)}")
                        logger.error(traceback.format_exc())
                        error_data = json.dumps({"error": f"处理事件错误: {str(e)}"})
                        yield f"event: error\ndata: {error_data}\n\n"
                else:
                    # 短暂等待，避免CPU过载
                    time.sleep(0.1)
        except GeneratorExit:
            # 浏览器关闭连接或客户端主动断开连接时会触发
            logger.info(f"Client disconnected: GeneratorExit for {client_id}")
            connection_closed = True
        except Exception as e:
            logger.error(f"Error in SSE stream for {client_id}: {str(e)}")
            logger.error(traceback.format_exc())
            connection_closed = True
        finally:
            # 当生成器关闭时，清理连接
            logger.info(f"SSE stream ended for client {client_id}, session {session_id}")
            with connection_lock:
                if client_id in active_connections:
                    del active_connections[client_id]
            
            # 如果这是session的最后一个连接，通知agent_service
            # 检查是否还有其他连接使用相同的session_id
            has_other_connections = False
            with connection_lock:
                for _, sess_id in active_connections.items():
                    if sess_id == session_id:
                        has_other_connections = True
                        break
            
            if not has_other_connections:
                logger.info(f"No more connections for session {session_id}, marking as disconnected")
                agent_service.handle_client_disconnect(session_id)
    
    # 设置响应头，确保SSE连接不会被缓存
    response = Response(generate(), mimetype="text/event-stream")
    response.headers['Cache-Control'] = 'no-cache, no-transform'
    response.headers['Connection'] = 'keep-alive'
    response.headers['X-Accel-Buffering'] = 'no'  # 禁用Nginx缓冲
    return response

@app.route('/api/agents/<session_id>/interrupt', methods=['POST'])
def interrupt_agent(session_id):
    """中断正在运行的 agent 任务"""
    try:
        if session_id not in agent_service.agent_instances:
            return jsonify({"error": "Agent not found"}), 404
            
        logger.info(f"Interrupting agent {session_id}")
        success = agent_service.interrupt_agent(session_id)
        
        if success:
            return jsonify({"status": "interrupted", "session_id": session_id})
        else:
            return jsonify({"error": "Failed to interrupt agent"}), 500
    except Exception as e:
        logger.error(f"Error interrupting agent {session_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=8000, 
        threaded=True
    )
