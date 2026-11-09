
import re

import streamlit as st

from api_client import ask_assistant, get_transaction_details

st.set_page_config(
    page_title="AI Banking Operations Assistant",
    page_icon="🏦",
    layout="wide",
)

st.title("🏦 AI Banking Operations Assistant")
st.caption(
    "Investigate banking transactions using "
    "transaction data and AI-powered assistance."
)

with st.sidebar:
    st.header("Banking Operations")
    st.write("Transaction Investigation Assistant")
    st.divider()
    st.subheader("About")
    st.write(
        "An assistant that helps banking operations "
        "teams investigate transactions."
    )

# Initialize session state.
if "messages" not in st.session_state:
    st.session_state.messages = []

if "last_transaction" not in st.session_state:
    st.session_state.last_transaction = None


def display_transaction_details(transaction: dict) -> None:
    """Display structured transaction information."""

    st.subheader("Transaction Overview")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Transaction Amount",
        f"₹{float(transaction['amount']):,.2f}",
    )

    col2.metric(
        "Transaction Status",
        transaction["transaction_status"],
    )

    col3.metric(
        "Payment Channel",
        transaction["payment_channel"],
    )

    st.divider()

    st.subheader("Transaction Details")

    details_col1, details_col2 = st.columns(2)

    with details_col1:
        st.write("**Transaction Reference**")
        st.write(transaction["transaction_reference"])

        st.write("**Transaction Type**")
        st.write(transaction["transaction_type"])

        st.write("**Failure Code**")
        st.write(transaction["failure_code"] or "N/A")

        st.write("**Failure Reason**")
        st.write(transaction["failure_reason"] or "N/A")

    with details_col2:
        st.write("**Customer Name**")
        st.write(
            f"{transaction['first_name']} "
            f"{transaction['last_name']}"
        )

        st.write("**Account Number**")
        st.write(transaction["account_number"])

        st.write("**Account Balance**")
        st.write(f"₹{float(transaction['balance']):,.2f}")

        st.write("**Account Status**")
        st.write(transaction["account_status"])


# Display the most recently retrieved transaction.
if st.session_state.last_transaction:
    display_transaction_details(st.session_state.last_transaction)

st.divider()
st.subheader("Transaction Investigation Assistant")

# Display existing conversation history.
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

user_prompt = st.chat_input(
    "Ask about a transaction or enter its reference..."
)

if user_prompt:
    st.session_state.messages.append(
        {"role": "user", "content": user_prompt}
    )

    with st.chat_message("user"):
        st.markdown(user_prompt)

    with st.chat_message("assistant"):
        with st.spinner("Investigating your request..."):
            try:
                # Detect whether the user entered only a transaction reference.
                transaction_reference = user_prompt.strip()

                is_transaction_reference = bool(
                    re.fullmatch(
                        r"TXN[A-Z0-9]{8,}",
                        transaction_reference,
                        re.IGNORECASE,
                    )
                )

                if is_transaction_reference:
                    # Retrieve structured transaction data.
                    transaction = get_transaction_details(
                        transaction_reference
                    )

                    st.session_state.last_transaction = transaction

                    # Ask Gemini to investigate the retrieved transaction.
                    assistant_response = ask_assistant(
                        
                            f"Investigate transaction "
                            f"{transaction_reference}. "
                            "Explain its status, identify any failure "
                            "reason or inconsistencies, and recommend "
                            "appropriate investigation steps."
                        
                    )

                else:
                    # Handle natural-language questions.
                    assistant_response = ask_assistant(user_prompt)

                st.markdown(assistant_response)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": assistant_response,
                    }
                )

            except ValueError as error:
                error_message = str(error)
                st.warning(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": f"**Unable to process request:** {error_message}",
                    }
                )

            except Exception:
                error_message = (
                    "Something went wrong while processing your request. "
                    "Please check that the backend is running and try again."
                )

                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )