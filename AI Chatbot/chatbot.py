import streamlit as st
import requests
import json
import time
from PyPDF2 import PdfReader


# Initialize session state variables
if "page" not in st.session_state:
    st.session_state["page"] = "New chat"
if "sidebar_visible" not in st.session_state:
    st.session_state.sidebar_visible = True
if "all_chats" not in st.session_state:
    st.session_state.all_chats = []
if "current_chat_index" not in st.session_state:
    # langsung buat chat pertama otomatis
    st.session_state.all_chats.append([])
    st.session_state.current_chat_index = 0
if "messages" not in st.session_state:
    st.session_state.messages = st.session_state.all_chats[st.session_state.current_chat_index]



def get_response(prompt, selected_model_id, temperature, max_tokens):  
    api_key = st.session_state.api_key
    if not api_key:
        st.error("Please enter your API key first.")
        return None
    try:
        response = requests.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
                "HTTP-Referer": "http://localhost:8501",
                "X-Title": "AI Chatbot Streamlit"
            },
            json={
                "model": selected_model_id,
                "messages": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
            },
            timeout=30
        )

        if response.status_code != 200:
            try:
                error_msg = response.json().get("error", {}).get("message", response.text)
            except:
                error_msg = response.text
            st.error(f"⚠️ Model Error ({response.status_code}): {error_msg}")
            return "⚠️ AI unable to generate response"

        data = response.json()
        answer = data["choices"][0]["message"]["content"]
        return answer

    except requests.exceptions.Timeout:
        st.error("⚠️ Request timeout. Try again.")
        return "⚠️ Request timeout. Try again."

    except requests.exceptions.ConnectionError:
        st.error("⚠️ Unable to connect to the model server. Please check your internet connection.")
        return "⚠️ Unable to connect to the model server. Please check your internet connection."

    except Exception:
        return "⚠️ AI unable to generate response"


def typing_effect(text):
    placeholder = st.empty()
    msg = ""
    for char in text:
        msg += char
        placeholder.markdown(msg)
        time.sleep(0.015)
    return msg

def read_uploaded_file(uploaded_file):
    if uploaded_file.type == "text/plain":
        return uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        pdf_reader = PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    else:
        st.warning("❌ Unsupported file type. Please upload .txt or .pdf")
        return None


def newChat(selected_model_id, temperature, max_tokens):
    st.title("🤖 AI Chatbot")

    # Pastikan messages ada
    idx = st.session_state.current_chat_index
    if idx is None or idx >= len(st.session_state.all_chats):
        st.session_state.all_chats.append([])
        st.session_state.current_chat_index = len(st.session_state.all_chats) - 1
    st.session_state.messages = st.session_state.all_chats[st.session_state.current_chat_index]

    # Tampilkan semua chat yang sudah ada
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

    # Input + upload file sticky di bawah
    st.markdown(
        """
        <style>
        .bottom-bar {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            border-top: 1px solid #ddd;
            padding: 10px;
            z-index: 999;
            display: flex;
            gap: 10px;
        }
        .bottom-bar > div {
            flex: 1;
        }
        </style>
        """, unsafe_allow_html=True
    )
    st.markdown('<div class="bottom-bar">', unsafe_allow_html=True)

    # Input user
    prompt = st.chat_input("Type your message here...")

    # Upload file
    uploaded_file = st.file_uploader("", type=["txt", "pdf"], label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    # Handle file upload jika ada
    handle_file_upload(selected_model_id, temperature, max_tokens, uploaded_file)

    # Handle input user
    handle_text_chat(selected_model_id, temperature, max_tokens, prompt)



def handle_file_upload(selected_model_id, temperature, max_tokens, uploaded_file):
    # ================== Handle File Upload ==================
    if uploaded_file:
        file_content = read_uploaded_file(uploaded_file)
        if file_content:
            st.session_state.messages.append({
                "role": "user",
                "content": f"📄 I uploaded a file. Please summarize it:\n\n{file_content[:2000]}..."
            })
            with st.chat_message("user"):
                st.markdown("📄 Uploaded a file!")

            response = st.chat_message("assistant")
            with st.spinner("📖 Reading and summarizing file..."):
                message_for_api = st.session_state.messages.copy()
                answer = get_response(message_for_api, selected_model_id, temperature, max_tokens)
                if answer:
                    with response:
                        bot_text = typing_effect(answer)
                    st.session_state.messages.append({"role": "assistant", "content": bot_text})
                else:
                    st.error("Error: Unable to get response from the model.")


def handle_text_chat(selected_model_id, temperature, max_tokens, prompt):
    if not prompt:
        return

    # Append user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    idx = st.session_state.current_chat_index
    st.session_state.all_chats[idx] = st.session_state.messages

    # Tampilkan user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Tampilkan AI response
    response = st.chat_message("assistant")
    with st.spinner("🤔 Generating response..."):
        answer = get_response(st.session_state.messages, selected_model_id, temperature, max_tokens)
        if answer:
            with response:
                st.markdown(answer)
            st.session_state.messages.append({"role": "assistant", "content": answer})
            st.session_state.all_chats[idx] = st.session_state.messages
        else:
            st.error("Error: Unable to get response from the model.")


# ================== History Page ==================

def history(selected_model_id, temperature, max_tokens):
    st.title("📜 Chat History")

    # Loop chat history sekali saja
    if "messages" in st.session_state and st.session_state.messages:
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
    else:
        st.info("Belum ada chat history.")

    # Sticky bottom input
    st.markdown(
        """
        <style>
        .bottom-input {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: white;
            padding: 10px 20px;
            border-top: 1px solid #ddd;
            z-index: 999;
            display: flex;
            gap: 10px;
        }
        .bottom-input > div {
            flex: 1;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    st.markdown('<div class="bottom-input">', unsafe_allow_html=True)

    prompt = st.chat_input("Type your message here...")
    uploaded_file = st.file_uploader("📂", type=["txt", "pdf"], label_visibility="collapsed")

    st.markdown('</div>', unsafe_allow_html=True)
    st.divider()

    handle_file_upload(selected_model_id, temperature, max_tokens, uploaded_file)
    handle_text_chat(selected_model_id, temperature, max_tokens, prompt)



# ================== Sidebar Settings ==================
def sidebar():
    with st.sidebar:
            
        st.header("⚙️ Settings")

        # inisialisasi all_chats
        if "all_chats" not in st.session_state:
            st.session_state.all_chats = []
        if "current_chat_index" not in st.session_state:
            st.session_state.current_chat_index = None

        # tombol buat chat baru
        if st.button("➕ New Chat", key="new_chat", use_container_width=True):
            st.session_state.all_chats.append([])  # buat chat kosong
            st.session_state.current_chat_index = len(st.session_state.all_chats) - 1
            st.session_state.messages = st.session_state.all_chats[st.session_state.current_chat_index]
            st.session_state.page = "New chat"

        # daftar chat history
        st.subheader("💬 Chat History")
        if st.session_state.all_chats:
            for i, chat in enumerate(st.session_state.all_chats):
                if chat:  
                    title = chat[0]["content"][:40] + "..." if len(chat[0]["content"]) > 40 else chat[0]["content"]
                else:
                    title = f"Chat {i+1}"

                with st.container():
                    col1, col2 = st.columns([5, 1])
                    with col1:
                        if st.button(f"{title}", key=f"chat_{i}", use_container_width=True):
                            st.session_state.current_chat_index = i
                            st.session_state.page = "history"
                    with col2:
                        if st.button("🗑️", key=f"clear_chat_{i}"):
                            st.session_state.all_chats.pop(i)
                            if st.session_state.current_chat_index == i:
                                st.session_state.current_chat_index = i - 1 if i > 0 else None
                                st.session_state.page = "New chat"

                    st.markdown("---")  # garis pemisah antar chat
        else:
            st.info("Belum ada chat")

        # settings model
        st.subheader("⚙️ Model Settings")
        model_option = {
            "Auto Router (fallback pintar)": "openrouter/auto",
            "Mistral 7B (free)": "mistralai/mistral-7B-Instruct:free"
        }
        selected_model = st.selectbox("Select Model", options=list(model_option.keys()), index=0)
        selected_model_id = model_option[selected_model]

        if "api_key" not in st.session_state:
            st.session_state.api_key = ""
        st.session_state.api_key = st.text_input(
            "Enter your OpenRouter API Key:", 
            type="password", 
            value=st.session_state.api_key
            )
        temperature = st.slider("Temperature", 0.0, 1.5, 0.7, 0.1)
        max_tokens = st.slider("Max Tokens", 100, 4000, 1000, 100)

    return selected_model_id, temperature, max_tokens

# ================== Main Page Logic ==================
if st.session_state.sidebar_visible:
    selected_model_id, temperature, max_tokens = sidebar()

if st.session_state.page == "history":
    if st.session_state.current_chat_index is not None and 0 <= st.session_state.current_chat_index < len(st.session_state.all_chats):
        st.session_state.messages = st.session_state.all_chats[st.session_state.current_chat_index]
        history(selected_model_id, temperature, max_tokens)
    else:
        st.warning("Invalid chat index. Please select a valid chat from the history.")

if st.session_state.page == "New chat" and selected_model_id is not None:
    if st.session_state.current_chat_index is not None and 0 <= st.session_state.current_chat_index < len(st.session_state.all_chats):
        st.session_state.messages = st.session_state.all_chats[st.session_state.current_chat_index]
    else:
        st.session_state.messages = []  
    newChat(selected_model_id, temperature, max_tokens)