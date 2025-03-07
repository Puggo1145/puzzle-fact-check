from neo4j import GraphDatabase
from utils import get_env


URI = get_env("NEO4J_URI")
AUTH = (
    get_env("NEO4J_USERNAME"), 
    get_env("NEO4J_PASSWORD")
)

with GraphDatabase.driver(URI, auth=AUTH) as driver:
    driver.verify_connectivity()
