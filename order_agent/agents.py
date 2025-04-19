from typing import Annotated, Sequence, List, Literal
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, BaseMessage
from langgraph.types import Command
from langgraph.graph import MessagesState
from langgraph.prebuilt import create_react_agent
from langchain import hub
from langchain_community.agent_toolkits import SQLDatabaseToolkit

# Import shared resources
from config import llm, tavily_search
from database import db
from vectorstore import retriever

# --- Pydantic Models ---

class Format_document(BaseModel):
    """Format the retrieved documents."""
    extracted_field: str = Field(
        description="Extract the relevant field from the document.",
    )

class Supervisor(BaseModel):
    next: Literal["order", "web_search_node", "support", "human_node"] = Field(
        description="Determines which specialist to activate next in the workflow sequence: "
                    "'order' searches through the db using sql commands to give a proper response, "
                    "'support' when the user is looking for a specific information about license, terms and conditions, data privacy, etc., "
                    "'web_search_node' when asked about current or additional information available on the web, "
                    "'human_node' when none of the other agents are able to give a proper response, "
    )
    reason: str = Field(
        description="Detailed justification for the routing decision, explaining the rationale behind selecting the particular specialist and how this advances the task toward completion."
    )

class Validator(BaseModel):
    next: Literal["supervisor", "FINISH"] = Field(
        description="Specifies the next worker in the pipeline: 'supervisor' to continue or 'FINISH' to terminate."
    )
    reason: str = Field(
        description="The reason for the decision."
    )

# --- Agent Nodes ---

def supervisor_node(state: MessagesState) -> Command[Literal["order", "web_search_node", "support", "human_node"]]:
    system_prompt = ('''
        You are a workflow(Customer Support Inquiry Router and Responder) supervisor managing a team of four specialized agents: Order, web, support and human helper. Your role is to orchestrate the workflow by selecting the most appropriate next agent based on the current state and needs of the task. Provide a clear, concise rationale for each decision to ensure transparency in your decision-making process.

        **Team Members**:
        1. **Order**: Handles order-related inquiries, including order status, tracking, and modifications. This agent is equipped to search through the database using SQL commands to provide accurate information.
        2. **support**: Addresses frequently asked questions, such as license information, terms and conditions, and data privacy. This agent is knowledgeable about company policies and can provide detailed responses.
        3. **web_search_node**: Engages with users seeking current or additional information available on the web. This agent is adept at searching the internet for up-to-date information and resources.
        4. **human_node**: Acts as a fallback option when the other agents are unable to provide a satisfactory response. This agent is designed to handle complex inquiries that require human intervention or further escalation.

        **Your Responsibilities**:
        1. Analyze each user request and agent response for completeness, accuracy, and relevance.
        2. Route the task to the most appropriate agent at each decision point.
        3. Maintain workflow momentum by avoiding redundant agent assignments.
        4. Continue the process until the user's request is fully and satisfactorily resolved.

        Your objective is to create an efficient workflow that leverages each agent's strengths while minimizing unnecessary steps, ultimately delivering complete and accurate solutions to user requests.
    ''')
    messages = [{"role": "system", "content": system_prompt}] + state["messages"]
    response = llm.with_structured_output(Supervisor).invoke(messages)
    goto = response.next
    reason = response.reason
    print(f"--- Workflow Transition: Supervisor → {goto} ---")
    return Command(
        update={
            "messages": [
                HumanMessage(content=reason, name="supervisor")
            ]
        },
        goto=goto,
    )

def order_node(state: MessagesState) -> Command[Literal["validator"]]:
    """Handles order-related inquiries using SQL."""
    if not db:
        print("--- Order Node Error: Database not initialized. Skipping. ---")
        return Command(
            update={"messages": [HumanMessage(content="Database connection failed. Cannot process order request.", name="order_error")]},
            goto="validator",
        )

    prompt_template = hub.pull("langchain-ai/sql-agent-system-prompt")
    system_message = prompt_template.format(dialect="SQLite", top_k=5)
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)
    agent_executor = create_react_agent(llm, toolkit.get_tools(), prompt=system_message)
    result = agent_executor.invoke(state)
    print(f"--- Workflow Transition: Order Node → Validator ---")
    # Ensure the result message is a BaseMessage or convert it
    last_message = result["messages"][-1]
    if isinstance(last_message, BaseMessage):
        content = last_message.content
    elif isinstance(last_message, dict) and 'content' in last_message:
        content = last_message['content']
    else:
        content = str(last_message) # Fallback

    return Command(
        update={
            "messages": [
                HumanMessage(content=content, name="order")
            ]
        },
        goto="validator",
    )


def support_node(state: MessagesState) -> Command[Literal["validator"]]:
    """Handles support inquiries using the vector store."""
    if not retriever:
        print("--- Support Node Error: Retriever not initialized. Skipping. ---")
        return Command(
            update={"messages": [HumanMessage(content="Vector store not available. Cannot process support request.", name="support_error")]},
            goto="validator",
        )

    user_query = state["messages"][-1].content
    retrieved_docs = retriever.invoke(user_query)
    combined_content = "\\n\\n".join([doc.page_content for doc in retrieved_docs])
    print(f"--- Workflow Transition: Support Node → Validator ---")
    return Command(
        update={
            "messages": [
                HumanMessage(content=combined_content, name="support")
            ]
        },
        goto="validator",
    )

def web_search_node(state: MessagesState) -> Command[Literal["validator"]]:
    """Handles web search inquiries using Tavily."""
    research_agent = create_react_agent(
        llm,
        tools=[tavily_search],
        state_modifier="You are an Information Specialist with expertise in comprehensive research. Your responsibilities include:\\n\\n"
            "1. Identifying key information needs based on the query context\\n"
            "2. Gathering relevant, accurate, and up-to-date information from reliable sources\\n"
            "3. Organizing findings in a structured, easily digestible format\\n"
            "4. Citing sources when possible to establish credibility\\n"
            "5. Focusing exclusively on information gathering - avoid analysis or implementation\\n\\n"
            "Provide thorough, factual responses without speculation where information is unavailable."
    )
    result = research_agent.invoke(state)
    print(f"--- Workflow Transition: web_search → Validator ---")
    # Ensure the result message is a BaseMessage or convert it
    last_message = result["messages"][-1]
    if isinstance(last_message, BaseMessage):
        content = last_message.content
    elif isinstance(last_message, dict) and 'content' in last_message:
        content = last_message['content']
    else:
        content = str(last_message) # Fallback

    return Command(
        update={
            "messages": [
                HumanMessage(content=content, name="web_search_node")
            ]
        },
        goto="validator",
    )

def human_node(state: MessagesState) -> Command[Literal["supervisor"]]:
    """Handles cases requiring human input (placeholder for Streamlit input)."""
    # In a real application, this might involve waiting for user input via the UI.
    # For now, it returns a placeholder message indicating human intervention is needed.
    print(f"--- Workflow Transition: human_node → Supervisor ---")
    # This node might need adjustment depending on how Streamlit handles pauses/inputs.
    # For now, we'll just pass a message back to the supervisor.
    return Command(
        update={
            "messages": [
                HumanMessage(
                    content="Agent requires clarification or cannot proceed. Please provide more details or rephrase.",
                    name="human_node"
                )
            ]
        },
        goto="supervisor",
    )


def validator_node(state: MessagesState) -> Command[Literal["supervisor", "__end__"]]:
    """Validates the agent's answer against the user's question."""
    system_prompt = '''
        Your task is to ensure reasonable quality.
        Specifically, you must:
        - Review the user's question (the first message in the workflow).
        - Review the answer (the last message in the workflow).
        - If the answer addresses the core intent of the question, even if not perfectly, signal to end the workflow with 'FINISH'.
        - Only route back to the supervisor if the answer is completely off-topic, harmful, or fundamentally misunderstands the question.

        - Accept answers that are "good enough" rather than perfect
        - Prioritize workflow completion over perfect responses
        - Give benefit of doubt to borderline answers

        Routing Guidelines:
        1. 'supervisor' Agent: ONLY for responses that are completely incorrect or off-topic.
        2. Respond with 'FINISH' in all other cases to end the workflow.
    '''
    user_question = state["messages"][0].content
    agent_answer = state["messages"][-1].content

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_question},
        {"role": "assistant", "content": agent_answer},
    ]

    response = llm.with_structured_output(Validator).invoke(messages)
    goto = response.next
    reason = response.reason

    if goto == "FINISH":
        goto = "__end__" # Use LangGraph's END constant
        print(" --- Transitioning to END ---")
    else:
        print(f"--- Workflow Transition: Validator → Supervisor ---")

    return Command(
        update={
            "messages": [
                HumanMessage(content=reason, name="validator")
            ]
        },
        goto=goto,
    )