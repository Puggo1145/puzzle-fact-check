from dotenv import load_dotenv
load_dotenv()

from db import db_driver

records, summary, keys = db_driver.execute_query(
    "MATCH (p:Person {age: $age}) RETURN p.name AS name",
    age=42,
    database_="neo4j",
)

print(records)
