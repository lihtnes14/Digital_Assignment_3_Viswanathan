import streamlit as st
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from typing_extensions import TypedDict
from typing import Annotated
import os
from dotenv import load_dotenv

load_dotenv()

# Set API keys in the environment (or manually input if using secrets)

# Initialize LLM
llm = ChatGroq(
    api_key="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",
    model_name="gemma2-9b-it"
)

# Define State for LangGraph
class State(TypedDict):
    messages: Annotated[list, add_messages]

graph_builder = StateGraph(State)

# Node logic
def chatbot(state: State):
    return {"messages": llm.invoke(state["messages"])}

graph_builder.add_node("chatbot", chatbot)
graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", END)

graph = graph_builder.compile()

# Streamlit UI
st.set_page_config(page_title="Lendora Assistant", layout="wide")

# Add custom CSS for a modern and minimalistic design
st.markdown("""
    <style>
    /* Global Styles */
    body {
        font-family: 'Roboto', sans-serif;
        background-color: #f9f9f9;
        color: #333;
    }

    /* Chat Section */
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
        background-color: #fff;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        padding: 20px;
    }
    .stChatMessage {
        padding: 12px;
        border-radius: 10px;
        margin: 5px 0;
        font-size: 14px;
        line-height: 1.6;
    }
    .stChatMessage.user {
        background-color: #e0f7fa;
        text-align: left;
        margin-left: 0;
    }
    .stChatMessage.assistant {
        background-color: #f1f8e9;
        text-align: right;
        margin-right: 0;
    }

    /* Input Area */
    .stTextInput {
        border-radius: 20px;
        padding: 10px;
        font-size: 14px;
        width: 100%;
        border: 1px solid #ddd;
        margin-top: 10px;
    }

    /* Button */
    .stButton {
        background-color: #00796b;
        color: white;
        font-size: 16px;
        border-radius: 20px;
        padding: 12px 24px;
        width: 100%;
        border: none;
    }

    .stButton:hover {
        background-color: #004d40;
    }

    /* Title and Header */
    h1 {
        font-size: 2.5rem;
        color: #00796b;
        text-align: center;
    }
    h2 {
        font-size: 1.5rem;
        color: #333;
        text-align: center;
        margin-bottom: 30px;
    }

    .description {
        text-align: center;
        font-size: 1rem;
        color: #555;
        margin-bottom: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# App Title and Description
st.title("Lendora Assistant 🤖")
st.markdown("<h2>Your AI-powered Chat Assistant for Financial Support</h2>", unsafe_allow_html=True)
st.markdown('<p class="description">Ask me anything about financial assistance and I\'ll provide helpful responses. Let\'s chat!</p>', unsafe_allow_html=True)

# Initialize session state for chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to display chat history with role-based formatting
def display_chat_history():
    for role, message in st.session_state.chat_history:
        with st.chat_message(role):
            st.markdown(message)

# Chat input section with customized input box
user_input = st.text_input("Type your message here...", placeholder="Enter your message...", key="chat_input")

# Display chat history
display_chat_history()

# Process input and generate response
if user_input:
    st.session_state.chat_history.append(("user", user_input))
    with st.chat_message("user"):
        st.markdown(user_input)

    # Stream LangGraph response
    full_response = ""
    with st.chat_message("assistant"):
        response_box = st.empty()
        for event in graph.stream({"messages": [("user", user_input)]}):
            for value in event.values():
                if "messages" in value:
                    msg = value["messages"]
                    full_response = msg.content
                    response_box.markdown(full_response)

    st.session_state.chat_history.append(("assistant", full_response))

# Add a button for clearing the chat history
if st.button("Clear Chat History", key="clear_button", use_container_width=True):
    st.session_state.chat_history.clear()
    st.experimental_rerun()

