from dotenv import load_dotenv

from fastapi import FastAPI

load_dotenv()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

def main():
    pass
    
if __name__ == "__main__":
    main()
