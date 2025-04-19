\
# Multi-Agent Customer Support Assistant

## Overview

This project demonstrates a sophisticated multi-agent system designed to handle customer support inquiries. Built using LangGraph, LangChain, and Streamlit, it showcases advanced AI techniques for routing, information retrieval, and interaction. The system intelligently directs user queries to specialized agents (Order, Support, Web Search) or involves human intervention when necessary, providing a robust and scalable customer service solution.

This project serves as a portfolio piece demonstrating expertise in building complex AI workflows, integrating various data sources, and creating interactive user interfaces.

## Features & Skills Demonstrated

*   **Multi-Agent Workflow (LangGraph):**
    *   Implemented a stateful graph using LangGraph to manage the flow of conversation between different specialized agents.
    *   **Supervisor Agent:** A central router agent that analyzes the user query and directs it to the most appropriate specialist agent (Order, Support, Web Search) or escalates to human intervention based on predefined logic and LLM reasoning.
*   **Specialized Agents (LangChain):**
    *   **SQL Agent:** Handles database-related queries (e.g., order status, customer details) by interacting with an SQL database (`customer_orders.sql`) using LangChain's SQLDatabaseToolkit and a ReAct agent pattern.
    *   **RAG (Retrieval-Augmented Generation) Agent:** Answers support-related questions (e.g., policies, terms) by retrieving relevant information from a knowledge base (built using web scraping and a Chroma vector store with Google Generative AI embeddings).
    *   **Web Search Agent:** Fetches real-time information from the internet using the Tavily Search API for queries requiring current data.
*   **Human-in-the-Loop (Conceptual):**
    *   Includes a dedicated `human_node` in the graph. While the current implementation uses a basic placeholder, it demonstrates the architecture for incorporating human feedback or intervention into the workflow, crucial for handling ambiguous or complex queries agents cannot resolve.
*   **Structured Output & Validation:**
    *   Utilizes Pydantic models and LangChain's structured output capabilities to ensure agents (like the Supervisor and Validator) return responses in a specific, predictable format.
    *   Includes a `validator_node` to assess the quality and relevance of an agent's response before finalizing the workflow or routing back for refinement.
*   **Error Handling:**
    *   Incorporates checks for essential components like database connections (`database.py`) and vector store availability (`vectorstore.py`), providing informative messages if setup fails.
    *   The agent design inherently handles cases where specific tools might fail or return unexpected results.
*   **Interactive UI (Streamlit):**
    *   Provides a user-friendly web interface built with Streamlit (`app.py`) for users to interact with the multi-agent system in a chat-like format.
    *   Displays agent responses and manages chat history.
*   **Modular Code Structure:**
    *   Refactored from an initial Jupyter Notebook (`order_agent.ipynb`) into a well-organized structure with separate Python modules for configuration (`config.py`), database interactions (`database.py`), vector store setup (`vectorstore.py`), agent definitions (`agents.py`), graph definition (`graph.py`), and the Streamlit application (`app.py`).
*   **Environment Management:**
    *   Uses `python-dotenv` for secure management of API keys (`GOOGLE_API_KEY`, `TAVILY_API_KEY`).

## Technologies Used

*   **Core Framework:** LangChain, LangGraph
*   **LLM:** Google Gemini (via `langchain-google-genai`)
*   **Embeddings:** Google Generative AI Embeddings
*   **Vector Store:** ChromaDB (`langchain-chroma`)
*   **Web Search:** Tavily Search API (`langchain-tavily`)
*   **Database:** SQLite, SQLAlchemy (`langchain_community`)
*   **Web UI:** Streamlit
*   **Environment:** Python, `python-dotenv`
*   **Data Handling:** Pydantic

## Project Structure

```
langgraph/
├── order_agent/             # Original notebook logic refactored here
│   ├── agents.py            # Agent node definitions & Pydantic models
│   ├── app.py               # Streamlit application
│   ├── config.py            # API keys, LLM/tool initializations
│   ├── customer_orders.sql  # Sample database data
│   ├── database.py          # Database connection setup
│   ├── graph.py             # LangGraph definition and compilation
│   ├── vectorstore.py       # Vector store setup (RAG)
│   └── __pycache__/
├── .env                     # Environment variables (API Keys - Gitignored)
├── order_agent.ipynb        # Original Jupyter Notebook (for reference)
├── requirements.txt         # Project dependencies
└── README.md                # This file
```

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd langgraph
    ```
2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv env
    source env/bin/activate  # On Windows use `env\\Scripts\\activate`
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Set up Environment Variables:**
    *   Create a `.env` file in the `langgraph` directory.
    *   Add your API keys to the `.env` file:
        ```dotenv
        GOOGLE_API_KEY="YOUR_GOOGLE_API_KEY"
        TAVILY_API_KEY="YOUR_TAVILY_API_KEY"
        # Optional: For LangSmith tracing
        # LANGCHAIN_TRACING_V2="true"
        # LANGCHAIN_API_KEY="YOUR_LANGSMITH_API_KEY"
        # LANGCHAIN_PROJECT="Your-Project-Name"
        ```

## How to Run

1.  Ensure your virtual environment is activated.
2.  Navigate to the project directory (`langgraph/`).
3.  Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```
4.  Open your web browser and go to the local URL provided by Streamlit (usually `http://localhost:8501`).
5.  Interact with the assistant by typing your queries into the chat input.

## Future Improvements

*   **Refine Human-in-the-Loop:** Implement a proper mechanism for the `human_node` to pause execution and wait for actual user input via the Streamlit interface.
*   **Enhance Error Handling:** Add more specific error handling within agent nodes and provide clearer feedback to the user.
*   **Improve RAG:** Implement more advanced RAG techniques (e.g., query transformation, document re-ranking).
*   **Add Memory:** Incorporate conversation history memory for more context-aware interactions over multiple turns.
*   **Deployment:** Containerize the application (e.g., using Docker) for easier deployment.
