from neomodel import config  # type: ignore
from utils import get_env

USERNAME = get_env("NEO4J_USERNAME")
PASSWORD = get_env("NEO4J_PASSWORD")

config.DATABASE_URL = f"bolt://{USERNAME}:{PASSWORD}@localhost:7687"

from .integrations import AgentDatabaseIntegration
from .repository import (
    NewsTextRepository,
    SearchRepository,
    MetadataRepository,
    CheckPointRepository,
)
from .services import DatabaseService

# 初始化一个全局共享的 integration
db_integration = AgentDatabaseIntegration()

__all__ = [
    "db_integration",
    "NewsTextRepository",
    "SearchRepository",
    "MetadataRepository",
    "CheckPointRepository",
    "DatabaseService",
]
