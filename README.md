![Puzzle](./images/puzzle-cover.png)

# Puzzle
Puzzle is a self-reflective news fact-checking AI agent based on the idea of DeepSearch. By leveraging deep web search and reasoning across multiple evidences, Puzzle meticulously traces and validates news sources, empowering you to distinguish facts from fiction with confidence.

## 🔔 Update
The online version is temporarily suspended due to the high server costs to me. The frontend page is still remained but the backend is not available currently. To experience the full features, please deploy puzzle to your local machine. Thanks for your support.

## Features
- 🔍 Deep Search: Puzzle follows logical traces between news and evidences, and goes deeper and deeper until it reaches the truth.
- 🧠 Self-Reflective Reasoning: Puzzle thinks thoroughly before it takes next action. And it can adjust its strategy dynamically based on search results to align with the purpose.
- 📊 Multi-Agent Collaboration: Puzzle leverages multiple specialized agents working together, with one agent focusing on reasoning and others on executing actions to achieve optimal results.
- 📝 Reliable News Fact Check Methods: Puzzle always focuses on validatable and trustworthy sources and is loyal to first-hand materials.

## How it works
This is an illustration of how Puzzle works from a top-level view. (It might take some time to load this image)
![Puzzle](./images/agent-graph.png)

## Quick Start
### 1. configurate your models and services
go to puzzle/.env.example.

#### required:
**at least one base model (OpenAI, Qwen, DeepSeek, Gemini)**. 

You should input its API key and choose one or more different types of models. Puzzle separates model into: reasoning, non-reasoning and light models to support tasks with different complexity. You should configurate at least one model. For example:
```
# OpenAI
OPENAI_API_KEY=xxxxxxxxxxxxxx
OPENAI_API_KEY_THIRD_PARTY=
OPENAI_BASE_URL_THIRD_PARTY=
OPENAI_REASONING_MODELS=o4-mini
OPENAI_NON_REASONING_MODELS=gpt-4o
OPENAI_LIGHT_MODELS=gpt-4o-mini
```

For OpenAI model, you can choose to add between official apis or other providers like open router. For every model, we require a 

#### optional:
You can add some optional services like Google Search API and Tavily Search to enhance the ability and performance of Puzzle. Not providing these services won't affect the operation of Puzzle since we have alternative tools for most of their functionalities. 
```
# Optional Services
# Tool Keys
TAVILY_API_KEY=
GOOGLE_SEARCH_API_KEY=
GOOGLE_CX_ID=
```

After finishing all your configuration, remember to rename the **.env.example** to **.env**

### 2. Install dependencies
#### 2.1 required environments
Puzzle requires Node.js and Python3. You should download them first.

#### 2.2 frontend dependencies
We recommand to use pnpm to manage dependencies. Using npm is also ok.

go to /web folder, and execute the command:
```
pnpm install
```

#### 2.3 backend dependencies
The backend uses poetry to manage dependencies. We recommand you to download poetry first.

go to /puzzle folder, and execute the command:
```
poetry install
```

### 3. run in development mode
#### 3.1 start the backend
go to /puzzle and run the command:
```
poetry run python -m api.app
```

#### 3.2 start the frontend
go to /web and run the command:
```
pnpm run dev
// or
npm run dev
```

This will open a dev server. Go to localhost:3000 in your browser

Enjoy Now! 😘
