from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import json
import time
import traceback
import logging
from typing import Dict, Any, List
import threading

from .service import agent_service

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

# 定义可用模型列表和限制
AVAILABLE_MODELS = {
    "openai": ["chatgpt-4o-latest", "gpt-4o", "gpt-4o-mini"],
    "qwen": ["qwq-plus-latest", "qwen-plus-latest", "qwen-turbo"],
    "deepseek": ["deepseek-reasoner", "deepseek-chat"]
}

# 定义不同Agent类型的模型限制
MODEL_RESTRICTIONS = {
    "main_agent": {
        "excluded": ["gpt-4o-mini", "qwen-turbo"]
    },
    "metadata_extractor": {
        "excluded": []  # 元数据提取器可以使用所有模型
    },
    "searcher": {
        "excluded": ["gpt-4o-mini", "qwen-turbo"]
    }
}

def validate_model_config(config: Dict[str, Any]) -> List[str]:
    """验证模型配置，返回错误消息列表"""
    errors = []
    
    # 验证创建Agent时的模型配置
    if "model_name" in config and "model_provider" in config:
        model_name = config["model_name"]
        model_provider = config["model_provider"]
        
        # 检查提供商是否支持
        if model_provider not in AVAILABLE_MODELS:
            errors.append(f"不支持的模型提供商: {model_provider}")
        else:
            # 检查模型是否在提供商的列表中
            if model_name not in AVAILABLE_MODELS[model_provider]:
                errors.append(f"模型 {model_name} 不在 {model_provider} 提供商的支持列表中")
    
    # 验证agent配置中的模型
    for agent_type in ["main_agent", "metadata_extractor", "searcher"]:
        if agent_type in config:
            agent_config = config[agent_type]
            if "model_name" in agent_config and "model_provider" in agent_config:
                model_name = agent_config["model_name"]
                model_provider = agent_config["model_provider"]
                
                # 检查提供商是否支持
                if model_provider not in AVAILABLE_MODELS:
                    errors.append(f"{agent_type} 使用了不支持的模型提供商: {model_provider}")
                else:
                    # 检查模型是否在提供商的列表中
                    if model_name not in AVAILABLE_MODELS[model_provider]:
                        errors.append(f"{agent_type} 使用的模型 {model_name} 不在 {model_provider} 提供商的支持列表中")
                    
                    # 检查是否有agent类型的特定限制
                    if model_name in MODEL_RESTRICTIONS[agent_type]["excluded"]:
                        errors.append(f"模型 {model_name} 不能用于 {agent_type}")
    
    return errors

@app.route('/api/agents', methods=['POST'])
def create_agent():
    """创建一个新的 agent 实例"""
    try:
        config = request.json or {}
        logger.info(f"Creating agent with config: {config}")
        
        # 验证模型配置
        errors = validate_model_config(config)
        if errors:
            return jsonify({"errors": errors}), 400
        
        session_id = agent_service.create_agent(config)
        logger.info(f"Agent created with session_id: {session_id}")
        return jsonify({"session_id": session_id})
    except Exception as e:
        logger.error(f"Error creating agent: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/agents/<session_id>/run', methods=['POST'])
def run_agent(session_id):
    """启动 agent 执行流程"""
    data = request.json
    if not data or 'news_text' not in data:
        logger.error(f"Missing required parameter: news_text for session {session_id}")
        return jsonify({"error": "Missing required parameter: news_text"}), 400
    
    news_text = data['news_text']
    config = data.get('config', {})
    logger.info(f"Running agent {session_id} with news_text: {news_text[:50]}...")
    
    # 验证模型配置
    errors = validate_model_config(config)
    if errors:
        return jsonify({"errors": errors}), 400
    
    try:
        agent_service.run_agent(session_id, news_text, config)
        return jsonify({"status": "running", "session_id": session_id})
    except ValueError as e:
        logger.error(f"Value error for session {session_id}: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error running agent {session_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

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
        try:
            while True:
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
                    # 如果没有事件，发送一个 heartbeat 事件保持连接
                    yield f"event: heartbeat\ndata: {json.dumps({'time': time.time()})}\n\n"
                    time.sleep(0.5)  # 避免 CPU 过载
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
                for conn_id, sess_id in active_connections.items():
                    if sess_id == session_id:
                        has_other_connections = True
                        break
            
            if not has_other_connections:
                logger.info(f"No more connections for session {session_id}, marking as disconnected")
                agent_service.handle_client_disconnect(session_id)
    
    return Response(generate(), mimetype="text/event-stream")

@app.route('/api/fact-check', methods=['POST'])
def create_and_run_agent():
    """创建一个新的 agent 实例并立即开始核查"""
    try:
        data = request.json
        if not data or 'news_text' not in data:
            logger.error("Missing required parameter: news_text")
            return jsonify({"error": "Missing required parameter: news_text"}), 400
        
        news_text = data['news_text']
        config = data.get('config', {})
        
        # 验证模型配置
        errors = validate_model_config(config)
        if errors:
            return jsonify({"errors": errors}), 400
        
        logger.info(f"Creating agent with config: {config}")
        session_id = agent_service.create_agent(config)
        if not session_id:
            logger.error("Failed to create agent: no session ID returned")
            return jsonify({"error": "Failed to create agent: no session ID returned"}), 500
            
        logger.info(f"Agent created with session_id: {session_id}")
        
        logger.info(f"Running agent {session_id} with news_text: {news_text[:50]}...")
        agent_service.run_agent(session_id, news_text, config)
        
        return jsonify({"status": "running", "session_id": session_id})
    except Exception as e:
        logger.error(f"Error in create_and_run_agent: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

# 返回API根目录的信息
@app.route('/api', methods=['GET'])
def api_info():
    logger.info("API info requested")
    return jsonify({
        "name": "Puzzle Fact Check API",
        "version": "1.0.0",
        "endpoints": [
            {"path": "/api/agents", "method": "POST", "description": "创建新的 agent 实例"},
            {"path": "/api/agents/<session_id>/run", "method": "POST", "description": "启动 agent 执行流程"},
            {"path": "/api/agents/<session_id>/interrupt", "method": "POST", "description": "中断正在运行的任务"},
            {"path": "/api/agents/<session_id>/events", "method": "GET", "description": "订阅 agent 事件流"},
            {"path": "/api/fact-check", "method": "POST", "description": "创建 agent 并直接开始核查"}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
