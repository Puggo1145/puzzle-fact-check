"""
Server for the Puzzle Fact Check API.
"""

import sys
import logging
import uvicorn
from dotenv import load_dotenv

load_dotenv()

# configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


if __name__ == "__main__":
    logger.info("Starting Puzzle Fact Check API service")
    reload = True
    if sys.platform.startswith("win"):
        reload = False
    uvicorn.run(
        "api:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=reload,
        log_level="info",
    )
