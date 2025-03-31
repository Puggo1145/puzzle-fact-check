import os
import logging
from dotenv import load_dotenv

load_dotenv()

if os.getenv("MODE") == "production":
    load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env.production'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("puzzle_api")