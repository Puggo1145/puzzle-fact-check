"""
Test for the service layer and SSE stream
"""
import asyncio
import time
from flask import Flask
from threading import Thread

from .test_agent import test_main_agent
from api.service import SSESession, get_session

# Create a minimal Flask app for testing
app = Flask(__name__)

async def process_test_agent_events(news_text: str, session_id: str, sse_session: SSESession):
    """Process events from the test agent's generator and add them to the SSE session"""
    try:
        # Add a starting event
        sse_session.add_event({
            "event": "agent_start",
            "data": {"message": "Agent starting"}
        })
        
        # Get events from the agent generator
        async for event_data in test_main_agent(news_text, session_id):
            # Forward event to SSE session
            sse_session.add_event(event_data)
            
            # Check for task completion
            if event_data.get("event") == "write_fact_check_report_end":
                # If we've generated the final report, we're close to done
                print("Final report generated, task nearly complete")
                
        # Add task complete event
        sse_session.add_event({
            "event": "task_complete",
            "data": {"message": "核查任务完成"}
        })
            
    except Exception as e:
        # Handle any exceptions
        error_message = f"Error running agent: {str(e)}"
        print(f"Exception in agent processing: {error_message}")
        sse_session.add_event({
            "event": "error",
            "data": {"message": error_message}
        })
    finally:
        # Close the SSE session when finished
        sse_session.close()

def run_test_agent(news_text: str, session_id: str):
    """Run the test agent in a separate thread and forward events to the SSE session"""
    # Get the session
    session = get_session(session_id)
    if not session:
        print(f"Session {session_id} not found")
        return
    
    sse_session = session["sse_session"]
    
    # Create event loop for the thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Run the agent processing coroutine
    loop.run_until_complete(
        process_test_agent_events(news_text, session_id, sse_session)
    )

@app.route('/test-sse')
def test_sse_endpoint():
    """Test the SSE session with a mock client"""
    # Create a new SSE session
    session_id = "test-session-1"
    sse_session = SSESession(session_id)
    
    # Start a thread to generate events
    Thread(target=generate_test_events, args=(sse_session,)).start()
    
    # Return SSE response
    return sse_session.get_response()

def generate_test_events(sse_session: SSESession):
    """Generate test events for the SSE session"""
    try:
        # Add some test events
        time.sleep(1)
        sse_session.add_event({"event": "test_event_1", "data": {"message": "Test event 1"}})
        time.sleep(1)
        sse_session.add_event({"event": "test_event_2", "data": {"message": "Test event 2"}})
        time.sleep(1)
        sse_session.add_event({"event": "test_event_3", "data": {"number": 42, "items": ["a", "b", "c"]}})
        time.sleep(1)
        sse_session.add_event({"event": "task_complete", "data": {"message": "Test complete"}})
    finally:
        # Close the session
        time.sleep(1)
        sse_session.close()

if __name__ == "__main__":
    from api.service import create_session
    
    # Test the service implementation with our test agent
    print("Creating test session...")
    session_id = create_session()
    print(f"Created session: {session_id}")
    
    # Start the agent in a separate thread
    agent_thread = Thread(target=run_test_agent, args=("OpenAI发布了全新的GPT-4模型", session_id))
    agent_thread.start()
    
    # Run a simple Flask server for SSE testing
    print("Starting Flask server on http://localhost:5000/")
    app.run(debug=False, port=5000, threaded=True)
    
    # Wait for the agent to finish
    agent_thread.join()
    print("Test complete") 