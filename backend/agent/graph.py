
from langchain_core.runnables import RunnableConfig
from langgraph.graph import END, START, StateGraph

from backend.agent.classifier import classify_request
from backend.agent.state import AgentState
from backend.tools.transaction_tools import lookup_transaction


def route_request(state: AgentState) -> str:
    """Choose the next graph node based on the classified intent."""
    intent = state["intent"]

    routes = {
        "transaction": "transaction_lookup",
        "account": "account_lookup",
        "clarification": "clarification",
        "fallback": "fallback",
    }

    return routes.get(intent, "fallback")


def transaction_lookup_node(
        state: AgentState,
        config: RunnableConfig,
) -> dict:
    """Retrieve transaction details using the approved banking tool."""

    db = config.get("configurable", {}).get("db")

    if db is None:
        return {
            "error": "Database session was not provided.",
            "response": "Unable to retrieve transaction details.",
        }

    transaction_reference = state["transaction_reference"]

    if not transaction_reference:
        return {
            "error": "Transaction reference is missing.",
            "response": "Please provide a valid transaction reference.",
        }

    result = lookup_transaction(
        db=db,
        transaction_reference=transaction_reference,
    )

    if not result["success"]:
        return {
            "transaction_data": None,
            "error": result["error"],
            "response": result["error"],
        }

    return {
        "transaction_data": result["data"],
        "error": None,
        "response": "Transaction details retrieved successfully.",
    }


def account_lookup_node(state: AgentState) -> dict:
    """Placeholder for account retrieval."""
    return {
        "response": (
            "Your request was classified as an account investigation. "
            "Account retrieval has not yet been connected."
        )
    }


def clarification_node(state: AgentState) -> dict:
    """Return a clarification request."""
    return {
        "response": state["error"]
                    or "Please provide more information about your request."
    }


def fallback_node(state: AgentState) -> dict:
    """Handle unsupported requests."""
    return {
        "response": state["error"]
                    or "I cannot handle this request."
    }


def build_assistant_graph():
    """Build and compile the banking assistant graph."""
    workflow = StateGraph(AgentState)

    workflow.add_node("classify_request", classify_request)
    workflow.add_node("transaction_lookup", transaction_lookup_node)
    workflow.add_node("account_lookup", account_lookup_node)
    workflow.add_node("clarification", clarification_node)
    workflow.add_node("fallback", fallback_node)

    workflow.add_edge(START, "classify_request")

    workflow.add_conditional_edges(
        "classify_request",
        route_request,
        {
            "transaction_lookup": "transaction_lookup",
            "account_lookup": "account_lookup",
            "clarification": "clarification",
            "fallback": "fallback",
        },
    )

    workflow.add_edge("transaction_lookup", END)
    workflow.add_edge("account_lookup", END)
    workflow.add_edge("clarification", END)
    workflow.add_edge("fallback", END)

    return workflow.compile()


assistant_graph = build_assistant_graph()
