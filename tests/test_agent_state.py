
from backend.agent.state import create_initial_state


def test_create_initial_state_sets_question():
    state = create_initial_state("Why did my payment fail?")

    assert state["question"] == "Why did my payment fail?"


def test_create_initial_state_has_expected_defaults():
    state = create_initial_state("Investigate transaction TXN12345678")

    assert state["intent"] is None
    assert state["customer_id"] is None
    assert state["transaction_reference"] is None
    assert state["transaction_data"] is None
    assert state["customer_data"] is None
    assert state["policy_context"] == []
    assert state["warnings"] == []
    assert state["response"] is None
    assert state["error"] is None


def test_initial_states_do_not_share_mutable_lists():
    first_state = create_initial_state("Question one")
    second_state = create_initial_state("Question two")

    first_state["warnings"].append("Test warning")
    first_state["policy_context"].append({"title": "Test SOP"})

    assert second_state["warnings"] == []
    assert second_state["policy_context"] == []
