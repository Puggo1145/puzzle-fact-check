from neomodel import config  # type: ignore
from utils import get_env

USERNAME = get_env("NEO4J_USERNAME")
PASSWORD = get_env("NEO4J_PASSWORD")

config.DATABASE_URL = f"bolt://{USERNAME}:{PASSWORD}@localhost:7687"

from neomodel import db as neo4j

__all__ = ["neo4j"]
