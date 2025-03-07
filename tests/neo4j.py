from dotenv import load_dotenv
load_dotenv()

from db import neo4j

results, meta = neo4j.cypher_query("RETURN 'HELLO WORLD' as message")
print(results, meta)
