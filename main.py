import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print(os.environ["QWEN_API_KEY"])


if __name__ == "__main__":
    main()
