from typing import TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, HumanMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

from src.config import OPENAI_API_KEY, MODEL_NAME
from src.database import run_query, SCHEMA_DESCRIPTION


# --- Tool ---
@tool
def sql_query(query: str) -> str:
    """
    Execute a read-only SQL SELECT query on the credit database.
    Use this to answer questions about borrowers, defaults, income, age, and credit risk.
    Only SELECT queries are allowed. The table is named 'borrowers'.
    """
    return run_query(query)


# --- LLM ---
llm = ChatOpenAI(model=MODEL_NAME, temperature=0, api_key=OPENAI_API_KEY)
llm_with_sql = llm.bind_tools([sql_query])


# --- System Prompt ---
SYSTEM_PROMPT = f"""You are a helpful data analyst assistant for a credit risk database.

You have access to a SQL database with the following schema:

{SCHEMA_DESCRIPTION}

When the user asks a question:
1. Write a SQL SELECT query to get the data
2. Use the sql_query tool to execute it
3. Interpret the results and give a clear, natural language answer

RULES:
- Only use SELECT queries
- Always use exact column names from the schema
- For percentages, calculate them in SQL using ROUND(100.0 * ... , 2)

HANDLING "AGE GROUPS":
When a user asks about "age groups", use CASE WHEN buckets, NOT individual ages:
  CASE WHEN age < 30 THEN '<30'
       WHEN age < 45 THEN '30-44'
       WHEN age < 60 THEN '45-59'
       ELSE '60+' END

STATISTICAL SIGNIFICANCE:
For "highest"/"lowest" rate questions, add HAVING COUNT(*) > 100 to avoid misleading outliers.
"""


# --- State ---
class AgentState(TypedDict):
    messages: Annotated[list, add_messages]


# --- Nodes ---
def call_llm(state: AgentState):
    response = llm_with_sql.invoke(state["messages"])
    return {"messages": [response]}


def call_tools(state: AgentState):
    last_message = state["messages"][-1]
    tool_messages = []
    for tool_call in last_message.tool_calls:
        result = sql_query.invoke(tool_call["args"])
        tool_messages.append(ToolMessage(
            content=str(result),
            tool_call_id=tool_call["id"]
        ))
    return {"messages": tool_messages}


def should_continue(state: AgentState) -> str:
    if state["messages"][-1].tool_calls:
        return "tools"
    return "end"


# --- Build graph ---
_builder = StateGraph(AgentState)
_builder.add_node("llm", call_llm)
_builder.add_node("tools", call_tools)
_builder.add_edge(START, "llm")
_builder.add_conditional_edges("llm", should_continue, {"tools": "tools", "end": END})
_builder.add_edge("tools", "llm")
sql_agent = _builder.compile()


# --- Public function ---
def ask_agent(question: str) -> str:
    """Ask the SQL agent a question, return the natural language answer."""
    result = sql_agent.invoke({
        "messages": [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=question)
        ]
    })
    return result["messages"][-1].content