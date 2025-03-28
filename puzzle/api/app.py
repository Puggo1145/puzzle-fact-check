from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import json
import time
import traceback
import logging
from typing import Dict, Any

from .service import agent_service

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('puzzle_api')

app = Flask(__name__)
CORS(app)  # 启用 CORS 以支持前端跨域调用

@app.route('/api/agents', methods=['POST'])
def create_agent():
    """创建一个新的 agent 实例"""
    try:
        config = request.json or {}
        logger.info(f"Creating agent with config: {config}")
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
    logger.info(f"Running agent {session_id} with news_text: {news_text[:50]}...")
    
    try:
        agent_service.run_agent(session_id, news_text)
        return jsonify({"status": "running", "session_id": session_id})
    except ValueError as e:
        logger.error(f"Value error for session {session_id}: {str(e)}")
        return jsonify({"error": str(e)}), 404
    except Exception as e:
        logger.error(f"Error running agent {session_id}: {str(e)}")
        logger.error(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/agents/<session_id>/events', methods=['GET'])
def get_agent_events(session_id):
    """
    SSE 接口，返回 agent 执行过程中的事件流
    前端可以通过 EventSource 订阅这个接口接收实时事件
    """
    logger.info(f"Client connected to SSE stream for session {session_id}")
    
    def generate():
        event_count = 0
        while True:
            # 获取队列中的事件，如果没有则等待一段时间
            event = agent_service.get_events(session_id)
            if event:
                event_count += 1
                event_type = event["event"]
                logger.info(f"Sending event {event_count} of type {event_type} for session {session_id}")
                
                # 确保数据可以被JSON序列化
                try:
                    data = json.dumps(event["data"])
                    yield f"event: {event_type}\ndata: {data}\n\n"
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
    
    return Response(generate(), mimetype="text/event-stream")

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
            {"path": "/api/agents/<session_id>/events", "method": "GET", "description": "订阅 agent 事件流"}
        ]
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000, threaded=True)
