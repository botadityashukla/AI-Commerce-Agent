# Multi-Agent AI Customer Support (GenAI Portfolio)

A production-style Multi-Agent Customer Support System built with **LangGraph**, **FastAPI**, and **Docker**. This project demonstrates advanced RAG pipelines, agentic routing, and observability.

![System Architecture](https://via.placeholder.com/800x400?text=System+Architecture+Diagram)
*(Note: Replace with actual screenshot/diagram later)*

## 🚀 Features

- **Multi-Agent Routing**: Intelligently routes queries to FAQ, Escalation, or Summary agents using LangGraph.
- **RAG Pipeline**: Local FAISS vector database + SentenceTransformers for accurate knowledge retrieval.
- **Sentiment Analysis**: Detects user frustration and automatically escalates to a support ticket.
- **Observability**: Structured JSON logging and decision tracing.
- **Production Ready**: Fully Dockerized with CI/CD workflows and type-safe Python code.

## 🛠 Tech Stack

- **Backend**: Python 3.10+, FastAPI, LangGraph, LangChain
- **AI/ML**: Google Gemini (via API), FAISS (Vector DB), SentenceTransformers
- **Frontend**: Vanilla JS, HTML5, CSS3
- **DevOps**: Docker, Docker Compose, GitHub Actions

## 📂 Project Structure

```text
support-ai/
├── backend/
│   ├── main.py                 # FastAPI Entrypoint
│   ├── agents/                 # Agent Implementations
│   ├── rag/                    # Vector Database & Loader
│   ├── core/                   # Router & Logger
│   └── config.py               # Settings
├── frontend/                   # Single Page Application
├── data/                       # Knowledge Base
└── docker-compose.yml          # Container Orchestration
```

## 🔧 Setup & Installation

### Prerequisites
- Docker & Docker Compose
- Google Gemini API Key (or Groq/OpenRouter)

### Quick Start

1.  **Clone the repository**
2.  **Configure Environment**
    ```bash
    cp .env.example .env
    # Edit .env and add your GEMINI_API_KEY
    ```
3.  **Run with Docker**
    ```bash
    cd support-ai
    docker-compose up --build
    ```
4.  **Access the App**
    - Frontend: `http://localhost:80`
    - API Docs: `http://localhost:8000/docs`

## 🧠 Agent Architecture

The system uses a **Router Agent** to classify user intent:

1.  **FAQ Agent**: Handles general questions using RAG (Retrieval Augmented Generation) from `knowledge.txt`.
2.  **Escalation Agent**: Triggered by negative sentiment. "I want to speak to a human" or "This is broken!". Creates a support ticket.
3.  **Summary Agent**: Summarizes the conversation at the end of the session.

## 📊 API Endpoints

- `POST /chat`: Chat with the AI agents.
- `POST /ticket`: Create a support ticket manually.
- `GET /health`: System health check (LLM provider + Vector DB status).
- `GET /logs`: View system logs and agent decisions.

---
*Built for GenAI Engineering Portfolio.*
