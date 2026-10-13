import streamlit as st
import os
import time
import sqlite3
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

# ----------------- DATABASE SETUP (SQLite for True Multi-User Sync) -----------------
def init_db():
    conn = sqlite3.connect("nexuschat.db", check_same_thread=False)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            phone TEXT PRIMARY KEY,
            name TEXT,
            pin TEXT,
            contacts TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT,
            receiver TEXT,
            text TEXT,
            time TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

def get_db_connection():
    return sqlite3.connect("nexuschat.db", check_same_thread=False)

# ----------------- SESSION STATE & PERSISTENCE SETUP -----------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_phone" not in st.session_state:
    st.session_state.current_phone = ""
if "current_name" not in st.session_state:
    st.session_state.current_name = ""
if "theme_mode" not in st.session_state:
    st.session_state.theme_mode = "Dark"
if "active_chat_phone" not in st.session_state:
    st.session_state.active_chat_phone = "AI_ASSISTANT"

# Recover session from query parameters if page is refreshed
if not st.session_state.logged_in and "session_phone" in st.query_params:
    saved_phone = st.query_params["session_phone"]
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE phone = ?", (saved_phone,))
    res = cursor.fetchone()
    conn.close()
    if res:
        st.session_state.logged_in = True
        st.session_state.current_phone = saved_phone
        st.session_state.current_name = res[0]

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
            login_phone = st.text_input("Mobile Number", placeholder="e.g., 7012233906", key="login_phone_box").strip()
            login_pin = st.text_input("Security PIN", type="password", placeholder="Enter 4-digit PIN", key="login_pin_box").strip()
            
            if st.button("Log In to NexusChat", use_container_width=True):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("SELECT name, pin FROM users WHERE phone = ?", (login_phone,))
                user_record = cursor.fetchone()
                conn.close()
                
                if user_record:
                    db_name, db_pin = user_record
                    if db_pin == login_pin:
                        st.session_state.logged_in = True
                        st.session_state.current_phone = login_phone
                        st.session_state.current_name = db_name
                        st.query_params["session_phone"] = login_phone
                        st.success(f"Welcome back, {db_name}!")
                        time.sleep(0.6)
                        st.rerun()
                    else:
                        st.error("Incorrect security PIN.")
                else:
                    st.error("Mobile number not registered. Please create an account first.")

        # --- CREATE ACCOUNT TAB ---
        with auth_tab2:
            st.subheader("Register New Account")
            reg_name = st.text_input("Your Full Name", placeholder="e.g., Aagney", key="reg_name_box").strip()
            reg_phone = st.text_input("Mobile Number", placeholder="e.g., 7012233906", key="reg_phone_box").strip()
            reg_pin = st.text_input("Create Security PIN", type="password", placeholder="4-digit PIN", key="reg_pin_box").strip()
            
            if st.button("Create Account & Start", use_container_width=True):
                if not reg_name or not reg_phone or not reg_pin:
                    st.warning("Please fill out all fields.")
                else:
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    cursor.execute("SELECT phone FROM users WHERE phone = ?", (reg_phone,))
                    existing = cursor.fetchone()
                    
                    if existing:
                        st.error("An account with this mobile number already exists. Please log in.")
                        conn.close()
                    else:
                        cursor.execute("INSERT INTO users (phone, name, pin, contacts) VALUES (?, ?, ?, ?)", 
                                       (reg_phone, reg_name, reg_pin, ""))
                        conn.commit()
                        conn.close()
                        
                        st.session_state.logged_in = True
                        st.session_state.current_phone = reg_phone
                        st.session_state.current_name = reg_name
                        st.query_params["session_phone"] = reg_phone
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

# ----------------- SIDEBAR CONTROLS -----------------
with st.sidebar:
    st.title("💬 Chats")
    st.markdown(f"👤 **{st.session_state.current_name}** (`{st.session_state.current_phone}`)")
    
    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.session_state.theme_mode = st.selectbox("Theme", ["Dark", "Light"], index=0 if st.session_state.theme_mode == "Dark" else 1, label_visibility="collapsed")
    with col_s2:
        if st.button("🔒 Log Out", use_container_width=True):
            if "session_phone" in st.query_params:
                del st.query_params["session_phone"]
            st.session_state.logged_in = False
            st.rerun()
            
    st.markdown("---")
    st.subheader("➕ Add Contact")
    search_number = st.text_input("Mobile Number:", placeholder="e.g., 7293332211", label_visibility="collapsed").strip()
    
    if st.button("Add to Chat List", use_container_width=True):
        if search_number == st.session_state.current_phone:
            st.warning("Cannot add your own number.")
        else:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT name, contacts FROM users WHERE phone = ?", (search_number,))
            target_user = cursor.fetchone()
            
            if target_user:
                target_name = target_user[0]
                cursor.execute("SELECT contacts FROM users WHERE phone = ?", (st.session_state.current_phone,))
                my_record = cursor.fetchone()
                current_contacts = my_record[0].split(",") if my_record[0] else []
                
                if search_number not in current_contacts:
                    current_contacts.append(search_number)
                    updated_contacts_str = ",".join(current_contacts)
                    cursor.execute("UPDATE users SET contacts = ? WHERE phone = ?", (updated_contacts_str, st.session_state.current_phone))
                    conn.commit()
                    conn.close()
                    st.success(f"Added **{target_name}** successfully!")
                    time.sleep(0.4)
                    st.rerun()
                else:
                    conn.close()
                    st.info("Already in contacts.")
            else:
                conn.close()
                st.error("User not found in database.")

    st.markdown("---")
    st.markdown("### Recent Conversations")
    
    if st.button("🤖 Nexus AI Assistant\n*Stealth Assistant*", key="chat_ai", use_container_width=True):
        st.session_state.active_chat_phone = "AI_ASSISTANT"
        st.rerun()
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT contacts FROM users WHERE phone = ?", (st.session_state.current_phone,))
    res = cursor.fetchone()
    my_contacts = res[0].split(",") if res and res[0] else []
    
    for contact_phone in my_contacts:
        if contact_phone:
            cursor.execute("SELECT name FROM users WHERE phone = ?", (contact_phone,))
            c_res = cursor.fetchone()
            if c_res:
                contact_name = c_res[0]
                is_active = st.session_state.active_chat_phone == contact_phone
                btn_label = f"🟢 {contact_name}\n📞 {contact_phone}" if is_active else f"👤 {contact_name}\n📞 {contact_phone}"
                
                if st.button(btn_label, key=f"wa_chat_{contact_phone}", use_container_width=True):
                    st.session_state.active_chat_phone = contact_phone
                    st.rerun()
    conn.close()

# ----------------- DETERMINE ACTIVE CHAT TITLE -----------------
if st.session_state.active_chat_phone == "AI_ASSISTANT":
    active_chat_title = "🤖 Nexus AI Assistant"
else:
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM users WHERE phone = ?", (st.session_state.active_chat_phone,))
    t_res = cursor.fetchone()
    conn.close()
    active_chat_title = t_res[0] if t_res else "Chat"

st.markdown(f"""
    <div class="nexus-header">
        <div>
            <h2 style="margin: 0; padding: 0;">{active_chat_title}</h2>
            <span style="font-size: 0.85em; color: #00a884;">● End-to-End Encrypted Chat</span>
        </div>
    </div>
""", unsafe_allow_html=True)

tab_chat, tab_calls, tab_status = st.tabs(["💬 Chat & Stealth AI", "📞 HD Voice & Video Calls", "🌟 Status Feed"])

# --- TAB 1: REAL-TIME CHAT & MESSAGING ---
with tab_chat:
    if st.session_state.active_chat_phone == "AI_ASSISTANT":
        st.write("Chatting with your personal AI assistant.")
        
        if "ai_chats" not in st.session_state:
            st.session_state.ai_chats = []

        for msg in st.session_state.ai_chats:
            if msg["role"] == "user":
                st.markdown(f'<div class="user-msg"><b>You:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-msg"><b>Nexus AI:</b><br>{msg["content"]}</div>', unsafe_allow_html=True)

        if user_prompt := st.chat_input("Type a message..."):
            st.session_state.ai_chats.append({"role": "user", "content": user_prompt})
            
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
                        
            st.session_state.ai_chats.append({"role": "assistant", "content": final_answer})
            st.rerun()

    else:
        friend_phone = st.session_state.active_chat_phone
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM users WHERE phone = ?", (friend_phone,))
        f_res = cursor.fetchone()
        friend_name = f_res[0] if f_res else friend_phone
        
        st.write(f"Direct messaging with **{friend_name}** (`{friend_phone}`)")
        
        cursor.execute("""
            SELECT sender, text, time FROM messages 
            WHERE (sender = ? AND receiver = ?) OR (sender = ? AND receiver = ?)
            ORDER BY id ASC
        """, (st.session_state.current_phone, friend_phone, friend_phone, st.session_state.current_phone))
        room_messages = cursor.fetchall()
        conn.close()

        for sender, text, timestamp in room_messages:
            if sender == st.session_state.current_phone:
                st.markdown(f'<div class="user-msg"><b>You ({timestamp}):</b><br>{text}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="bot-msg"><b>{friend_name} ({timestamp}):</b><br>{text}</div>', unsafe_allow_html=True)

        if peer_prompt := st.chat_input(f"Message {friend_name}..."):
            timestamp = datetime.now().strftime("%H:%M")
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("INSERT INTO messages (sender, receiver, text, time) VALUES (?, ?, ?, ?)",
                           (st.session_state.current_phone, friend_phone, peer_prompt, timestamp))
            conn.commit()
            conn.close()
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