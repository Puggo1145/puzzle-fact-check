from neo4j import GraphDatabase
from utils import get_env


URI = get_env("NEO4J_URI")
AUTH = (
    get_env("NEO4J_USERNAME"), 
    get_env("NEO4J_PASSWORD")
)

db_driver = GraphDatabase.driver(URI, auth=AUTH)
db_driver.verify_connectivity()

__all__ = [
    "db_driver"
]

