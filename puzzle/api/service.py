import asyncio
import json
import threading
import uuid
import time
from api import logger

from typing import Dict, Optional, Any, Generator
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from flask import Response

from .model import CreateAgentConfig
from .agent_service import run_main_agent
from .events import (
    TaskComplete, 
    TaskInterrupted, 
    InterruptData,
    Error, 
    ErrorData,
)

# Thread pool executor for running agents in background
thread_pool = ThreadPoolExecutor(max_workers=5)

# Store active sessions
active_sessions: Dict[str, Dict[str, Any]] = {}
# Lock for thread-safe operations on sessions
sessions_lock = threading.Lock()

HEARTBEAT_INTERVAL = 30  # seconds

class SSESession:
    """Manages a Server-Sent Events session for a specific agent instance"""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.queue = Queue()
        self.is_running = True
        self.is_interrupted = False
        self.task: Optional[asyncio.Task] = None
    
    def add_event(self, event_data: Dict[str, Any]) -> None:
        """Add an event to the session's queue
        
        Args:
            event_data: A dictionary with 'event' and 'data' keys
        """
        if not self.is_running:
            return
        
        event_type = event_data.get('event')    
        self.queue.put(event_data)
        logger.info(f"Event added to queue: {event_type}")
        
        # Special logging for error events to help debug
        if event_type == 'error':
            logger.error(f"ERROR EVENT DETAILS: {json.dumps(event_data)}")
            logger.info(f"Queue size after adding error: {self.queue.qsize()}")
            
            # Force a small delay to ensure event processing
            time.sleep(0.2)
    
    def close(self) -> None:
        """Close the session and stop accepting new events"""
        # Don't immediately close if we've just added an error event
        # This ensures error events are processed before closing
        if not self.queue.empty():
            try:
                # Check if the last event in queue is an error
                # We can't easily peek at the last item without removing it
                # so we'll add a small delay for any non-empty queue
                time.sleep(0.5)  # Give time for events to be sent
            except Exception as e:
                logger.error(f"Error checking queue before closing: {e}")
                
        self.is_running = False
    
    def interrupt(self) -> bool:
        """Set the interrupted flag and close the session"""
        if not self.is_running:
            return False
        
        self.is_interrupted = True
        self.add_event(
            TaskInterrupted(data=InterruptData(message="核查任务被用户中断"))
            .model_dump()
        )
        self.close()
        return True
    
    def get_response(self) -> Response:
        """Create a streaming response for SSE events"""
        return Response(
            self._event_stream(),
            mimetype='text/event-stream',
            headers={
                'Cache-Control': 'no-cache, no-transform',
                'Connection': 'keep-alive',
                'X-Accel-Buffering': 'no',  # Disable Nginx buffering
                'Transfer-Encoding': 'chunked'  # Use chunked transfer to avoid buffering
            }
        )
    
    def _event_stream(self) -> Generator[str, None, None]:
        """Generate SSE formatted events from the queue with immediate flushing"""
        # First send a heartbeat event to establish the connection
        yield "event: heartbeat\ndata: {\"message\": \"Connection established\"}\n\n"
        
        last_heartbeat = time.time()
        
        # Flag to track if an error event was sent and needs a delay before closing
        error_sent = False
        error_sent_time = 0
        
        logger.info(f"Starting event stream for session {self.session_id}")
        
        while self.is_running or error_sent:
            current_time = time.time()
            
            # Check if we should exit after error delay
            if error_sent and (current_time - error_sent_time >= 2.0):  # Increased to 2 second delay after error
                logger.info("Error delay period ended, closing stream after error")
                error_sent = False
                break
            
            # Send heartbeat if needed
            if current_time - last_heartbeat >= HEARTBEAT_INTERVAL:
                yield "event: heartbeat\ndata: {\"message\": \"Connection alive\"}\n\n"
                last_heartbeat = current_time
                logger.info("Heartbeat sent")
            
            # Check for events (non-blocking)
            try:
                if not self.queue.empty():
                    event = self.queue.get(block=False)
                    event_type = event.get("event")
                    event_data = event.get("data")
                    
                    logger.info(f"Processing event from queue: {event_type}")
                    
                    try:
                        # Ensure data is JSON serializable
                        data_json = json.dumps(event_data) if event_data is not None else "{}"
                        message = f"event: {event_type}\ndata: {data_json}\n\n"
                        logger.info(f"Sending event: {event_type}")
                        
                        # Special handling for error events
                        if event_type == "error":
                            logger.error(f"Sending ERROR event: {data_json}")
                            yield message  # Send error event
                            error_sent = True
                            error_sent_time = current_time
                            logger.info("Error event sent, will delay closing connection")
                            # Force flush with a small yield
                            yield ""
                        else:
                            yield message
                        
                    except TypeError as e:
                        logger.error(f"Error serializing event data: {e}")
                else:
                    # Short sleep to avoid CPU spinning while checking for new events
                    time.sleep(0.1)
                    
            except Exception as e:
                logger.error(f"Error generating SSE event: {e}")
                time.sleep(0.5)  # Add delay on error
        
        logger.info(f"Exiting event stream loop for session {self.session_id}")
        
        # Final event to indicate the stream is closed - ALWAYS send this
        logger.info("Sending stream_closed event")
        yield "event: stream_closed\ndata: {\"message\": \"Stream closed\"}\n\n"
        # Force flush
        yield ""
        logger.info("Stream closed event sent")


def create_session() -> str:
    """Create a new agent session"""
    session_id = str(uuid.uuid4())
    
    with sessions_lock:
        active_sessions[session_id] = {
            "sse_session": SSESession(session_id),
            "is_running": False,
            "start_time": None
        }
    
    return session_id

def get_session(session_id: str) -> Optional[Dict[str, Any]]:
    """Get a session by ID"""
    with sessions_lock:
        return active_sessions.get(session_id)

def close_session(session_id: str) -> bool:
    """Close a session and clean up resources"""
    with sessions_lock:
        session = active_sessions.get(session_id)
        if not session:
            return False
        
        sse_session: SSESession = session["sse_session"]
        sse_session.close()
        
        # Remove session after a delay to allow final events to be delivered
        def delayed_removal():
            time.sleep(5)  # Wait 5 seconds
            with sessions_lock:
                active_sessions.pop(session_id, None)
        
        threading.Thread(target=delayed_removal).start()
        return True

def interrupt_session(session_id: str) -> bool:
    """Interrupt a running agent session"""
    with sessions_lock:
        session = active_sessions.get(session_id)
        if not session:
            return False
        
        sse_session: SSESession = session["sse_session"]
        return sse_session.interrupt()

async def process_agent_events(news_text: str, config: CreateAgentConfig, session_id: str, sse_session: SSESession):
    """Process events from the agent's generator and add them to the SSE session"""
    error_occurred = False
    
    try:
        # Add a starting event
        sse_session.add_event({
            "event": "agent_start",
            "data": {"message": "Agent starting"}
        })
        
        # Get events from the agent generator
        async for event_data in run_main_agent(news_text, config, session_id):
            # Forward event to SSE session
            sse_session.add_event(event_data)
                
        # Add task complete event
        sse_session.add_event(TaskComplete().model_dump())
            
    except Exception as e:
        # Handle any exceptions
        error_occurred = True
        error_message = f"Error running agent: {str(e)}"
        logger.error(f"Exception in agent processing: {error_message}")
        
        try:
            # Add error event and wait to ensure it's processed
            sse_session.add_event(
                Error(data=ErrorData(message=error_message))
                .model_dump()
            )
            
            # Add a delay to ensure error event is sent before closing
            await asyncio.sleep(1)
        except Exception as inner_e:
            # If we can't send the error event, at least log it
            logger.error(f"Error sending error event: {inner_e}")
        
    finally:
        try:
            # Delay before closing to allow final events to be sent
            await asyncio.sleep(0.5)
            
            # Make sure a stream_closed event is explicitly added if we had an error
            # This makes it more likely the browser will receive it
            if error_occurred:
                sse_session.add_event({
                    "event": "stream_closed",
                    "data": {"message": "Stream closed due to error"}
                })
                # Extra delay for error case
                await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"Error in final cleanup: {e}")
        
        # Close the SSE session when finished
        sse_session.close()

def run_agent_thread(news_text: str, config: CreateAgentConfig, session_id: str) -> None:
    """Run the agent in a separate thread and forward events to the SSE session"""
    session = get_session(session_id)
    if not session:
        return
    
    sse_session: SSESession = session["sse_session"]
    
    # Update session state
    with sessions_lock:
        session["is_running"] = True
        session["start_time"] = time.time()
    
    try:
        # Create event loop for the thread
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Run the agent processing coroutine
        loop.run_until_complete(
            process_agent_events(news_text, config, session_id, sse_session)
        )
        
    except Exception as e:
        # Handle any exceptions
        error_message = f"Error in agent thread: {str(e)}"
        logger.error(f"Exception in agent thread: {error_message}")
        
        # Add error event
        sse_session.add_event(
            Error(data=ErrorData(message=error_message))
            .model_dump()
        )
        
        # Allow time for error event to be processed
        time.sleep(1)
        
    finally:
        # Update session state
        with sessions_lock:
            if session_id in active_sessions:
                active_sessions[session_id]["is_running"] = False
                
        # Small delay to allow any final events to be sent
        time.sleep(0.5)

def start_agent(news_text: str, config: CreateAgentConfig) -> str:
    """Start a new agent instance and return the session ID"""
    session_id = create_session()
    
    # Start agent in background thread
    thread_pool.submit(run_agent_thread, news_text, config, session_id)
    
    return session_id
