import streamlit as st
import os
import time
import google.genai as genai
from datetime import datetime

# Page Configuration
st.set_page_config(
    page_title="NexusChat - Secure Messaging Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Key Configuration
GEMINI_API_KEY = "AQ.Ab8RN6JtKg-9BzUbcpA9vAmQrxI4WZl7cfCc0Q2efZ3lyi2kNA"

# ----------------- GLOBAL SHARED STATE SETUP -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_phone" not in st.session_state:
    st.session_state.current_phone = ""
if "current_name" not in st.session_state:
    st.session_state.current_name = ""

# Shared Global Database across connected users
if "global_users" not in st.session_state:
    st.session_state.global_users = {
        "9999999999": {"name": "Nexus Support", "pin": "0000", "contacts": []}
    }

# Shared Global Message Store
if "global_messages" not in st.session_state:
    st.session_state.global_messages = {}

if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"
if "active_chat_phone" not in st.session_state:
    st.session_state.active_chat_phone = "AI_ASSISTANT"

# Hardcoded Local Intelligence Database for AI
LOCAL_QA = {
    "hello": "Hello! Welcome to NexusChat. How can I assist you today?",
    "hi": "Hey there! Ready to chat or test out my knowledge base?",
    "who are you": "I am Nexus, your personal AI companion built straight into your secure chat network.",
    "features": "NexusChat includes mobile number authentication, live cross-user messaging, phone book contact addition, voice/video call rooms, and stealth AI assistance."
}

# ----------------- AUTHENTICATION GATE -----------------
if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center;'>⚡ NexusChat</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #9ca3af;'>Secure Real-Time Encrypted Messaging Platform</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    with col2:
        auth_tab1, auth_tab2 = st.tabs(["🔑 Log In", "✨ Create Account"])
        
        # --- LOGIN TAB ---
        with auth_tab1:
            st.subheader("Sign In")
            login_phone = st.text_input("Mobile Number", placeholder="e.g., 1234567890", key="login_phone_box").strip()
            login_pin = st.text_input("Security PIN", type="password", placeholder="Enter 4-digit PIN", key="login_pin_box").strip()
            
            if st.button("Log In to NexusChat", use_container_width=True):
                if login_phone in st.session_state.global_users:
                    if st.session_state.global_users[login_phone]["pin"] == login_pin:
                        st.session_state.logged_in = True
                        st.session_state.current_phone = login_phone
                        st.session_state.current_name = st.session_state.global_users[login_phone]["name"]
                        st.success(f"Welcome back, {st.session_state.current_name}!")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("Incorrect security PIN.")
                else:
                    st.error("Mobile number not registered. Please create an account first.")

        # --- CREATE ACCOUNT TAB ---
        with auth_tab2:
            st.subheader("Register New Account")
            reg_name = st.text_input("Your Full Name", placeholder="e.g., Sarah Connor", key="reg_name_box").strip()
            reg_phone = st.text_input("Mobile Number", placeholder="e.g., 9876543210", key="reg_phone_box").strip()
            reg_pin = st.text_input("Create Security PIN", type="password", placeholder="4-digit PIN", key="reg_pin_box").strip()
            
            if st.button("Create Account & Start", use_container_width=True):
                if not reg_name or not reg_phone or not reg_pin:
                    st.warning("Please fill out all fields.")
                elif reg_phone in st.session_state.global_users:
                    st.error("An account with this mobile number already exists. Please log in.")
                else:
                    st.session_state.global_users[reg_phone] = {
                        "name": reg_name,
                        "pin": reg_pin,
                        "contacts": []
                    }
                    st.session_state.logged_in = True
                    st.session_state.current_phone = reg_phone
                    st.session_state.current_name = reg_name
                    st.success(f"Account created! Welcome, {reg_name}!")
                    time.sleep(0.6)
                    st.rerun()
                    
    st.stop()

# ----------------- MAIN APP STYLING & INTERFACE -----------------
if st.session_state.theme_mode == "Dark":
    bg_main = "#0b141a"
    bg_sidebar = "#111b21"
    bg_bubble_user = "#005c4b"
    bg_bubble_bot = "#202c33"
    text_color = "#e9edef"
    border_color = "#222d34"
else:
    bg_main = "#f0f2f5"
    bg_sidebar = "#ffffff"
    bg_bubble_user = "#d9fdd3"
    bg_bubble_bot = "#ffffff"
    text_color = "#111b21"
    border_color = "#e9edef"

st.markdown(f"""
    <style>
    .stApp {{
        background-color: {bg_main};
        color: {text_color};
    }}
    [data-testid="stSidebar"] {{
        background-color: {bg_sidebar};
        border-right: 1px solid {border_color};
    }}
    .nexus-header {{
        display: flex;
        align-items: center;
        background-color: {bg_sidebar};
        padding: 15px 20px;
        border-bottom: 1px solid {border_color};
        border-radius: 12px;
        margin-bottom: 20px;
    }}
    .user-msg {{
        background-color: {bg_bubble_user};
        color: {text_color};
        padding: 12px 16px;
        border-radius: 12px 12px 2px 12px;
        margin-left: auto;
        max-width: 75%;
        margin-bottom: 10px;
        box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
    }}
    .bot-msg {{
        background-color: {bg_bubble_bot};
        color: {text_color};
        padding: 12px 16px;
        border-radius: 12px 12px 12px 2px;
        margin-right: auto;
        max-width: 75%;
        margin-bottom: 10px;
        border: 1px solid {border_color};
        box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
    }}
    </style>
""", unsafe_allow_html=True)

# ----------------- SIDEBAR CONTROLS (WHATSAPP STYLE CHAT LIST) -----------------
with st.sidebar:
    st.title("💬 Chats")
    st.markdown(f"👤 **{st.session_state.current_name}** (`{st.session_state.current_phone}`)")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.session_state.theme_mode = st.selectbox("Theme", ["Dark", "Light"], index=0 if st.session_state.theme_mode == "Dark" else 1, label_visibility="collapsed")
    with col_s2:
        if st.button("🔒 Log Out", use_container_width=True):
            st.session_state.logged_in = False
            st.rerun()
            
    st.markdown("---")
    st.subheader("➕ Add Contact")
    search_number = st.text_input("Mobile Number:", placeholder="e.g., 1234567890", label_visibility="collapsed").strip()
    
    if st.button("Add to Chat List", use_container_width=True):
        if search_number == st.session_state.current_phone:
            st.warning("Cannot add your own number.")
        elif search_number in st.session_state.global_users:
            friend_contacts = st.session_state.global_users[st.session_state.current_phone]["contacts"]
            if search_number not in friend_contacts:
                friend_contacts.append(search_number)
                st.success(f"Added **{st.session_state.global_users[search_number]['name']}**!")
                time.sleep(0.4)
                st.rerun()
            else:
                st.info("Already in contacts.")
        else:
            st.error("User not found.")

    st.markdown("---")
    st.markdown("### Recent Conversations")
    
    # AI Assistant Row
    if st.button("🤖 Nexus AI Assistant\n*Stealth Assistant*", key="chat_ai", use_container_width=True):
        st.session_state.active_chat_phone = "AI_ASSISTANT"
        st.rerun()
        
    # Dynamic Contact Rows (Appears only when users are added)
    my_contacts = st.session_state.global_users[st.session_state.current_phone]["contacts"]
    for contact_phone in my_contacts:
        if contact_phone in st.session_state.global_users:
            contact_name = st.session_state.global_users[contact_phone]["name"]
            is_active = st.session_state.active_chat_phone == contact_phone
            btn_label = f"🟢 {contact_name}\n📞 {contact_phone}" if is_active else f"👤 {contact_name}\n📞 {contact_phone}"
            
            if st.button(btn_label, key=f"wa_chat_{contact_phone}", use_container_width=True):
                st.session_state.active_chat_phone = contact_phone
                st.rerun()

# ----------------- DETERMINE ACTIVE CHAT TITLE -----------------
if st.session_state.active_chat_phone == "AI_ASSISTANT":
    active_chat_title = "🤖 Nexus AI Assistant"
else:
    active_chat_title = st.session_state.global_users[st.session_state.active_chat_phone]["name"]

# Main Header
st.markdown(f"""
    <div class="nexus-header">
        <div>
            <h2 style="margin: 0; padding: 0;">{active_chat_title}</h2>
            <span style="font-size: 0.85em; color: #00a884;">● End-to-End Encrypted Chat</span>
        </div>
    </div>
""", unsafe_allow_html=True)

# Main Navigation Tabs
tab_chat, tab_calls, tab_status = st.tabs(["💬 Chat & Stealth AI", "📞 HD Voice & Video Calls", "🌟 Status Feed"])

# --- TAB 1: REAL-TIME CHAT & MESSAGING ---
with tab_chat:
    if st.session_state.active_chat_phone == "AI_ASSISTANT":
        st.write("Chatting with your personal AI assistant.")
        
        if "ai_chats" not in st.session_state.global_users[st.session_state.current_phone]:
            st.session_state.global_users[st.session_state.current_phone]["ai_chats"] = []
        ai_history = st.session_state.global_users[st.session_state.current_phone]["ai_chats"]

        for msg in ai_history:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-msg"><b>You:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-msg"><b>Nexus AI:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

        if user_prompt := st.chat_input("Type a message..."):
            ai_history.append({"role": "user", "content": user_prompt})
            
            clean_input = user_prompt.strip().lower()
            matched_reply = None
            for key, response in LOCAL_QA.items():
                if key in clean_input:
                    matched_reply = response
                    break
            
            if matched_reply:
                final_answer = matched_reply
            else:
                with st.spinner("Nexus is thinking..."):
                    time.sleep(0.6)
                    if GEMINI_API_KEY:
                        try:
                            client = genai.Client(api_key=GEMINI_API_KEY)
                            gemini_response = client.models.generate_content(
                                model="gemini-2.5-flash",
                                contents=user_prompt
                            )
                            final_answer = gemini_response.text
                        except Exception as err:
                            final_answer = f"Temporary error retrieving response: {str(err)}"
                    else:
                        final_answer = "API key not configured."
                        
            ai_history.append({"role": "assistant", "content": final_answer})
            st.rerun()

    else:
        friend_phone = st.session_state.active_chat_phone
        friend_name = st.session_state.global_users[friend_phone]["name"]
        
        st.write(f"Direct messaging with **{friend_name}** (`{friend_phone}`)")
        
        chat_room_key = tuple(sorted([st.session_state.current_phone, friend_phone]))
        if chat_room_key not in st.session_state.global_messages:
            st.session_state.global_messages[chat_room_key] = []
            
        room_messages = st.session_state.global_messages[chat_room_key]

        for msg in room_messages:
            if msg["sender"] == st.session_state.current_phone:
                st.markdown(f'<div class="user-msg"><b>You ({msg["time"]}):</b><br>{msg["text"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-msg"><b>{friend_name} ({msg["time"]}):</b><br>{msg["text"]}</div>', unsafe_allow_html=True)

        if peer_prompt := st.chat_input(f"Message {friend_name}..."):
            timestamp = datetime.now().strftime("%H:%M")
            room_messages.append({
                "sender": st.session_state.current_phone,
                "text": peer_prompt,
                "time": timestamp
            })
            st.rerun()

# --- TAB 2: VOICE & VIDEO CALLS ---
with tab_calls:
    st.subheader("📞 Direct Voice & Video Call Room")
    room_code = st.text_input("Enter Meeting Room Code:", "Nexus-Secure-Call-Room").strip()
    if room_code:
        call_url = f"https://meet.jit.si/{room_code}#config.prejoinPageEnabled=false"
        st.components.v1.iframe(call_url, height=580, scrolling=True)

# --- TAB 3: STATUS FEED ---
with tab_status:
    st.subheader("🌟 Status Feed")
    st.markdown(f"* **{st.session_state.current_name}**: *'Online on NexusChat.'* — Just now")
    new_status = st.text_input("Post a status update:")
    if st.button("Broadcast Status"):
        if new_status:
            st.success(f"Status posted: '{new_status}'")