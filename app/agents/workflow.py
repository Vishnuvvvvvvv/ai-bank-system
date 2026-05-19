from langgraph.graph import StateGraph

from app.agents.state import BankingState

from app.agents.intent_classifier import (
    classify_intent
)

from app.agents.supervisor import (
    supervisor_router
)
from langgraph.checkpoint.memory import (
    MemorySaver
)


workflow = StateGraph(BankingState)
memory = MemorySaver()

def intent_node(
    state: BankingState
):

    intent = classify_intent(
        state["query"]
    )

    if intent == "LOAN_APPLICATION":
        intent = "APPLY_LOAN"

    if intent == "TRANSFER_MONEY":
        intent = "MONEY_TRANSFER"

    state["intent"] = intent

    return state

from app.database.database import SessionLocal


async def supervisor_node(
    state: BankingState
):

    db = SessionLocal()

    try:

        workflow_data = state.get(
            "workflow_data",
            {}
        )

        result = await supervisor_router(
            db=db,
            query=state["query"],
            user_id=state["user_id"],
                intent=state["intent"],
            workflow_data=workflow_data
        )

        # ======================================
        # RETURN UPDATED STATE
        # ======================================

        return {

            **state,
              "intent": result.get(
        "intent",
        state.get("intent")
    ),
            "response": result,

            "workflow_data": result.get(
                "workflow_data",
                workflow_data
            )
        }

    finally:

        db.close()

workflow.add_node(
    "intent_classifier",
    intent_node
)

workflow.add_node(
    "supervisor",
    supervisor_node
)


workflow.set_entry_point(
    "intent_classifier"
)

workflow.add_edge(
    "intent_classifier",
    "supervisor"
)


graph = workflow.compile(checkpointer=memory)
