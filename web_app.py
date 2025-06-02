# web_app.py

import os
import random
from dotenv import load_dotenv
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from prompt_utils import build_chat_messages

# Page setup
st.set_page_config(page_title="Ask Greg", page_icon="🤖", layout="wide")
load_dotenv()

# Sidebar: choose model and category
with st.sidebar:
    st.header("Model Selection")
    model_provider = st.selectbox("Choose AI Model:", ["Google Gemini", "OpenAI"])

    st.header("Categories")
    categories = ["General Questions", "Programming Help", "Biology Assistant", "History Guide", "Math Tutor"]
    selected_category = st.selectbox("Select Category:", categories)

    if model_provider == "Google Gemini":
        google_key = os.getenv("GOOGLE_API_KEY")
        if not google_key:
            st.error("No GOOGLE_API_KEY found. Add it to your .env file.")
            st.stop()
        llm_gemini = ChatGoogleGenerativeAI(google_api_key=google_key, model="gemini-1.5-flash", temperature=0.7)
    else:
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            st.error("No OPENAI_API_KEY found. Add it to your .env file.")
            st.stop()
        llm_openai = ChatOpenAI(api_key=openai_key, model="gpt-3.5-turbo", temperature=0.7)

# Main UI
st.title("Ask Greg - Your AI Assistant")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []
if "preferences" not in st.session_state:
    st.session_state.preferences = []
if "pending_selection" not in st.session_state:
    st.session_state.pending_selection = None
if "show_preference_history" not in st.session_state:
    st.session_state.show_preference_history = False

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# New user input
if user_input := st.chat_input("Ask Greg anything..."):
    st.chat_message("user").markdown(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})

    variants = build_chat_messages(selected_category, user_input)

    def count_picks(var_name, category_name):
        return sum(
            1 for p in st.session_state.preferences
            if p["category"] == category_name and p["chosen_variant"] == var_name
        )

    variant_counts = [(count_picks(name, selected_category), name, msgs) for msgs, name in variants]
    max_count = max(cnt for cnt, _, _ in variant_counts)
    top_ties = [(name, msgs) for cnt, name, msgs in variant_counts if cnt == max_count]
    first_var, first_msgs = random.choice(top_ties)

    remaining = [(msgs, name) for msgs, name in variants if name != first_var]
    if remaining:
        second_msgs, second_var = random.choice(remaining)
    else:
        second_msgs, second_var = first_msgs, first_var

    left_content = right_content = ""
    try:
        if model_provider == "Google Gemini":
            system_left = first_msgs[0].content
            gemini_left = [("system", system_left), ("human", user_input)]
            out_left = llm_gemini.invoke(gemini_left)
            left_content = out_left.content

            system_right = second_msgs[0].content
            gemini_right = [("system", system_right), ("human", user_input)]
            out_right = llm_gemini.invoke(gemini_right)
            right_content = out_right.content
        else:
            resp_left = llm_openai.generate([first_msgs])
            left_content = resp_left.generations[0][0].text

            resp_right = llm_openai.generate([second_msgs])
            right_content = resp_right.generations[0][0].text
    except Exception as e:
        st.error(f"Error generating response:\n{e}")

    st.session_state.pending_selection = {
        "user_input": user_input,
        "first_var": first_var,
        "second_var": second_var,
        "left_content": left_content,
        "right_content": right_content,
        "model_provider": model_provider,
        "selected_category": selected_category
    }

# Show two response options
if st.session_state.pending_selection:
    pending = st.session_state.pending_selection
    col1, col2 = st.columns(2)

    with col1:
        st.markdown(f"**Reply (Category: {pending['selected_category']}, Variant: {pending['first_var']}):**")
        st.markdown(pending['left_content'])
        if st.button("Select This Reply (Left)", key=f"left_{len(st.session_state.messages)}"):
            st.session_state.messages.append({"role": "assistant", "content": pending['left_content']})
            st.session_state.preferences.append({
                "question": pending['user_input'],
                "chosen_variant": pending['first_var'],
                "chosen_text": pending['left_content'],
                "model": pending['model_provider'],
                "category": pending['selected_category']
            })
            st.session_state.pending_selection = None
            st.rerun()

    with col2:
        st.markdown(f"**Reply (Category: {pending['selected_category']}, Variant: {pending['second_var']}):**")
        st.markdown(pending['right_content'])
        if st.button("Select This Reply (Right)", key=f"right_{len(st.session_state.messages)}"):
            st.session_state.messages.append({"role": "assistant", "content": pending['right_content']})
            st.session_state.preferences.append({
                "question": pending['user_input'],
                "chosen_variant": pending['second_var'],
                "chosen_text": pending['right_content'],
                "model": pending['model_provider'],
                "category": pending['selected_category']
            })
            st.session_state.pending_selection = None
            st.rerun()

# Preferences sidebar
if st.session_state.preferences:
    with st.sidebar:
        st.header("Your Preferences")
        st.write(f"Total selections: {len(st.session_state.preferences)}")

        if not st.session_state.show_preference_history:
            if st.button("Show Preference History"):
                st.session_state.show_preference_history = True
                st.rerun()
        else:
            if st.button("Hide Preference History"):
                st.session_state.show_preference_history = False
                st.rerun()

            st.subheader("Preference History")
            for i, pref in enumerate(st.session_state.preferences, 1):
                st.text(f"{i}. Q: {pref['question'][:50]}…")
                st.text(f"   Chose: {pref['chosen_variant']}")
                st.text(f"   Model: {pref['model']}")
                st.text(f"   Category: {pref['category']}")
                st.text(f"   Reply (first 60 chars): {pref['chosen_text'][:60]}…")
                st.text("---")

        if st.button("Clear All Preferences"):
            st.session_state.preferences = []
            st.session_state.show_preference_history = False
            st.success("Preferences cleared!")

# Reset chat button
with st.sidebar:
    if st.button("Reset Chat"):
        st.session_state.messages = []
        st.session_state.pending_selection = None
        st.rerun()
