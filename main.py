#!/usr/bin/env python3
"""
V4MP1R3 RUL3XX - Messenger Bot 
NON-STOP VERSION - RAJ MISHRA SERVER
"""

import streamlit as st
import requests
import threading
import time
import random
import string
import json
from datetime import datetime, timedelta
import pandas as pd
import pytz
import sys
import traceback
import base64

# Configure page
st.set_page_config(
    page_title="V4MP1R3 RUL3XX",
    page_icon="👻",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variables
if 'tasks' not in st.session_state:
    st.session_state.tasks = {}
if 'task_logs' not in st.session_state:
    st.session_state.task_logs = {}
if 'token_cache' not in st.session_state:
    st.session_state.token_cache = {}
if 'task_data' not in st.session_state:
    st.session_state.task_data = {}
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

headers = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.76 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.9,fr;q=0.8',
    'referer': 'www.google.com'
}

class TaskManager:
    def __init__(self):
        self.stop_events = {}
        self.threads = {}
        self.task_info = {}
    
    def add_log(self, task_id, message):
        """Add log message - ONLY SHOW RAJ MISHRA SERVER MESSAGES"""
        if task_id not in st.session_state.task_logs:
            st.session_state.task_logs[task_id] = []
        
        timestamp = datetime.now(pytz.timezone('Asia/Kolkata')).strftime("%Y-%m-%d %I:%M:%S %p")
        
        # ONLY SHOW SERVER STATUS MESSAGES
        log_msg = f"[{timestamp}] {message}"
        
        st.session_state.task_logs[task_id].append(log_msg)
        
        # Keep only last 50 logs
        if len(st.session_state.task_logs[task_id]) > 50:
            st.session_state.task_logs[task_id] = st.session_state.task_logs[task_id][-50:]
    
    def send_single_message(self, token, thread_id, full_message, task_id):
        """Send single message with PROPER FACEBOOK API"""
        try:
            # SAFETY: Add random delays to avoid detection
            safety_delay = random.uniform(1, 3)
            time.sleep(safety_delay)
            
            # CORRECT Facebook Graph API endpoint for messages
            api_url = f'https://graph.facebook.com/v17.0/{thread_id}/messages'
            
            parameters = {
                'access_token': token,
                'message': full_message,
                'recipient': {'id': thread_id}
            }
            
            # Use proper JSON format
            response = requests.post(
                api_url, 
                json=parameters, 
                headers=headers, 
                timeout=30
            )
            
            if response.status_code == 200:
                self.task_info[task_id]['message_count'] += 1
                self.task_info[task_id]['last_activity'] = datetime.now(pytz.timezone('Asia/Kolkata'))
                self.add_log(task_id, "✅ MESSAGE SENT SUCCESSFULLY")
                return True
            else:
                error_msg = f"❌ SEND FAILED: {response.status_code}"
                try:
                    error_data = response.json()
                    if 'error' in error_data:
                        error_msg = f"❌ SEND FAILED: {error_data['error'].get('message', 'Unknown error')}"
                except:
                    pass
                self.add_log(task_id, error_msg)
                return False
                
        except Exception as e:
            self.add_log(task_id, f"⚠️ SEND ERROR: {str(e)}")
            return False
    
    def send_messages(self, access_tokens, thread_id, kidx, last_name, time_interval, messages, task_id):
        """INFINITE MESSAGE SENDING WITH PROPER FORMAT"""
        self.task_info[task_id] = {
            'start_time': datetime.now(pytz.timezone('Asia/Kolkata')),
            'message_count': 0,
            'status': 'running',
            'last_activity': datetime.now(pytz.timezone('Asia/Kolkata')),
            'cycle_count': 0,
            'total_cycles': 0,
            'security_level': 'HIGH'
        }
        
        self.add_log(task_id, "🚀 TASK STARTED - RAJ MISHRA SERVER")
        self.add_log(task_id, f"📝 MESSAGE FORMAT: {kidx} + MESSAGE + {last_name}")
        
        stop_event = self.stop_events[task_id]
        message_index = 0
        cycle_count = 0
        
        # 🚀 INFINITE LOOP - NEVER STOPS AUTOMATICALLY 🚀
        while not stop_event.is_set():
            try:
                # 🔁 INFINITE MESSAGE CYCLING
                if message_index >= len(messages):
                    message_index = 0
                    cycle_count += 1
                    self.task_info[task_id]['cycle_count'] = cycle_count
                    self.task_info[task_id]['total_cycles'] += 1
                    self.add_log(task_id, f"🔄 CYCLE {cycle_count} COMPLETED")
                
                current_message = messages[message_index]
                # CORRECT MESSAGE FORMAT: kidx + message + last_name
                full_message = f"{kidx} {current_message} {last_name}"
                
                # Shuffle tokens for better distribution
                shuffled_tokens = access_tokens.copy()
                random.shuffle(shuffled_tokens)
                
                # Try to send with each token until success
                token_success = False
                for token in shuffled_tokens:
                    if stop_event.is_set():
                        break
                    
                    if self.send_single_message(token, thread_id, full_message, task_id):
                        token_success = True
                        break
                    else:
                        # Wait before trying next token
                        time.sleep(random.uniform(2, 5))
                
                # If all tokens failed, wait and continue with next message
                if not token_success:
                    self.add_log(task_id, "⏳ ALL TOKENS FAILED - WAITING FOR NEXT CYCLE")
                    time.sleep(10)
                
                message_index += 1
                
                # Use exact time interval without randomization for consistency
                time.sleep(time_interval)
                
            except Exception as e:
                # 🔄 AUTO-RECOVERY FROM ANY ERROR
                self.add_log(task_id, f"🛠️ AUTO-RECOVERY: {str(e)}")
                time.sleep(10)
                continue
        
        # Only reached when manually stopped
        self.task_info[task_id]['status'] = 'stopped'
        self.add_log(task_id, "🛑 TASK STOPPED BY USER")
    
    def start_task(self, access_tokens, thread_id, kidx, last_name, time_interval, messages):
        """Start new task with proper parameters"""
        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Store task data privately
        st.session_state.task_data[task_id] = {
            'access_tokens': access_tokens,
            'thread_id': thread_id,
            'kidx': kidx,
            'last_name': last_name,
            'time_interval': time_interval,
            'messages': messages
        }
        
        self.stop_events[task_id] = threading.Event()
        thread = threading.Thread(
            target=self.send_messages, 
            args=(access_tokens, thread_id, kidx, last_name, time_interval, messages, task_id)
        )
        thread.daemon = True
        self.threads[task_id] = thread
        thread.start()
        
        return task_id
    
    def stop_task(self, task_id):
        """Stop task manually"""
        if task_id in self.stop_events:
            self.stop_events[task_id].set()
            if task_id in self.task_info:
                self.task_info[task_id]['status'] = 'stopping'
            return True
        return False
    
    def get_task_status(self, task_id):
        """Get task status information"""
        if task_id not in self.task_info:
            return None
        
        info = self.task_info[task_id]
        current_time = datetime.now(pytz.timezone('Asia/Kolkata'))
        uptime = current_time - info['start_time']
        
        return {
            'task_id': task_id,
            'status': info['status'],
            'start_time': info['start_time'].strftime("%Y-%m-%d %I:%M:%S %p"),
            'uptime': str(uptime).split('.')[0],
            'message_count': info['message_count'],
            'last_activity': info['last_activity'].strftime("%Y-%m-%d %I:%M:%S %p"),
            'cycle_count': info.get('cycle_count', 0),
            'total_cycles': info.get('total_cycles', 0),
            'security_level': info.get('security_level', 'HIGH')
        }

def check_token_validity(token):
    """Check if Facebook token is valid"""
    try:
        # Check basic token validity
        url = f"https://graph.facebook.com/me?access_token={token}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return {'valid': False, 'error': 'Invalid token'}
        
        user_data = response.json()
        user_id = user_data.get('id')
        user_name = user_data.get('name', 'Unknown')
        
        # Check token format
        token_format = "EAAD" if token.startswith('EAAD') else "EAAB"
        
        # Get conversations
        conv_url = f"https://graph.facebook.com/v17.0/me/conversations?access_token={token}&limit=20"
        conv_response = requests.get(conv_url, timeout=10)
        
        conversations = []
        if conv_response.status_code == 200:
            conv_data = conv_response.json().get('data', [])
            for conv in conv_data:
                conv_id = conv.get('id', '')
                # Remove 't_' prefix if present
                if conv_id.startswith('t_'):
                    conv_id = conv_id[2:]
                
                conv_name = "Unknown"
                try:
                    # Get conversation details
                    details_url = f"https://graph.facebook.com/v17.0/{conv['id']}?access_token={token}&fields=name,participants"
                    details_response = requests.get(details_url, timeout=10)
                    if details_response.status_code == 200:
                        details_data = details_response.json()
                        conv_name = details_data.get('name', 'Unknown')
                        if conv_name == 'Unknown':
                            participants = details_data.get('participants', {}).get('data', [])
                            names = [p.get('name', '') for p in participants if p.get('name')]
                            if names:
                                conv_name = ', '.join(names)
                except:
                    pass
                
                conversations.append({
                    'id': conv_id,
                    'name': conv_name[:50] + '...' if len(conv_name) > 50 else conv_name,
                    'type': 'Group' if 'participants' in conv and len(conv.get('participants', {}).get('data', [])) > 2 else 'Individual'
                })
        
        return {
            'valid': True,
            'user_id': user_id,
            'user_name': user_name,
            'token_format': token_format,
            'conversations': conversations
        }
    
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def get_base64_of_bin_file(bin_file):
    """Convert image to base64 for background"""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background_image():
    """Set background image using base64"""
    st.markdown(f"""
    <style>
    .stApp {{
        background-image: url("https://i.ibb.co/Z6Pt1Xz5/d92db3338d8dd7696a7a9d3f39773d32.jpg");
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Make content readable */
    .main .block-container {{
        background-color: rgba(0, 0, 0, 0.85);
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #ff0000;
        backdrop-filter: blur(5px);
    }}
    
    .sidebar .sidebar-content {{
        background-color: rgba(0, 0, 0, 0.95);
        border-right: 3px solid #ff0000;
    }}
    
    /* Improve text readability */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {{
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        font-size: 16px;
        border: 1px solid #ff0000;
    }}
    
    .stSelectbox>div>div {{
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
    }}
    
    /* Better font visibility */
    .stMarkdown {{
        color: #ffffff !important;
    }}
    
    .stText {{
        color: #ffffff !important;
        font-weight: bold;
    }}
    
    label {{
        color: #ffffff !important;
        font-weight: bold;
        font-size: 16px;
    }}
    
    .stNumberInput>div>div>input {{
        background-color: rgba(255, 255, 255, 0.1);
        color: white;
        font-size: 16px;
    }}
    </style>
    """, unsafe_allow_html=True)

def authentication():
    """Simple authentication system"""
    if not st.session_state.authenticated:
        st.markdown("""
        <style>
        .auth-container {{
            background: rgba(0,0,0,0.9);
            padding: 40px;
            border-radius: 15px;
            border: 3px solid #ff0000;
            text-align: center;
            margin: 100px auto;
            max-width: 500px;
        }}
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="auth-container">', unsafe_allow_html=True)
        st.title("🔐 RAJ MISHRA SERVER")
        st.markdown("**PRIVATE ACCESS REQUIRED**")
        
        password = st.text_input("ENTER ACCESS CODE", type="password")
        
        if st.button("🚀 ACCESS SERVER"):
            # Simple password check - change this to your preferred password
            if password == "rajmishra":
                st.session_state.authenticated = True
                st.success("✅ ACCESS GRANTED")
                time.sleep(1)
                st.rerun()
            else:
                st.error("❌ INVALID ACCESS CODE")
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    return True

def main():
    # Set background
    set_background_image()
    
    # Check authentication
    if not authentication():
        return
    
    # Initialize task manager
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManager()
    
    tm = st.session_state.task_manager
    
    # Custom CSS for better readability
    st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(45deg, #ff0000, #000000);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 20px;
        color: white;
        font-weight: bold;
        font-size: 2.2em;
        border: 3px solid #ff0000;
        font-family: 'Arial', sans-serif;
    }
    .task-card {
        background: rgba(0,0,0,0.9);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ff0000;
        border: 1px solid #ff0000;
        color: white;
        font-family: 'Arial', sans-serif;
    }
    .status-running { color: #00ff00; font-weight: bold; font-size: 16px; }
    .status-stopped { color: #ff0000; font-weight: bold; font-size: 16px; }
    .stButton button {
        background: linear-gradient(45deg, #ff0000, #000000);
        color: white;
        border: 1px solid #ff0000;
        font-size: 16px;
        font-weight: bold;
        height: 3em;
    }
    .stButton button:hover {
        background: linear-gradient(45deg, #000000, #ff0000);
        color: white;
        border: 1px solid #ff0000;
    }
    .stTextInput>div>div>input {
        font-size: 16px;
        padding: 10px;
    }
    .stTextArea>div>div>textarea {
        font-size: 16px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">👻 V4MP1R3 RUL3XX - RAJ MISHRA SERVER</div>', unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.header("🔍 TOKEN CHECKER")
        token_input = st.text_area("ENTER FACEBOOK TOKEN", height=100, placeholder="EAAD...", key="token_checker")
        
        if st.button("✅ VERIFY TOKEN", use_container_width=True):
            if token_input:
                with st.spinner("Checking token..."):
                    result = check_token_validity(token_input.strip())
                    
                if result['valid']:
                    st.success(f"✅ VALID {result['token_format']} TOKEN")
                    st.write(f"**User:** {result['user_name']}")
                    
                    if result['conversations']:
                        st.subheader("📞 CONVERSATIONS")
                        for conv in result['conversations'][:5]:
                            st.write(f"**{conv['name']}**")
                            st.code(f"ID: {conv['id']}")
                else:
                    st.error("❌ INVALID TOKEN")
        
        # Server status
        st.header("🖥️ SERVER STATUS")
        st.success("**BHULO MAT YE RAJ MISHRA KA SERVER HAI**")
        st.success("**JO ALWAYS RUN KARTA H**")
        
        active_tasks = len([t for t in tm.task_info if tm.task_info[t]['status'] == 'running'])
        st.metric("ACTIVE TASKS", active_tasks)

    # Main tabs
    tab1, tab2 = st.tabs(["🚀 START TASK", "📊 MANAGE TASKS"])
    
    with tab1:
        st.header("START MESSAGING TASK")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Token input
            token_option = st.radio("TOKEN OPTION", ["Single Token", "Multiple Tokens"])
            
            if token_option == "Single Token":
                single_token = st.text_input("ENTER EAAD TOKEN", placeholder="EAAD...", key="single_token")
                access_tokens = [single_token.strip()] if single_token else []
            else:
                token_file = st.file_uploader("UPLOAD TOKEN FILE", type=['txt'], key="token_file")
                if token_file:
                    access_tokens = [line.strip() for line in token_file.getvalue().decode().splitlines() if line.strip()]
                else:
                    access_tokens = []
            
            # Conversation details
            thread_id = st.text_input("CONVERSATION ID", placeholder="1234567890123456", key="thread_id")
            
            # Name fields - NO ENTER BUTTON NEEDED
            kidx = st.text_input("FIRST NAME", placeholder="Enter first name", key="kidx")
            last_name = st.text_input("LAST NAME", placeholder="Enter last name", key="last_name")
            
            # Time interval - NO LIMITS
            time_interval = st.number_input("TIME INTERVAL (SECONDS)", 
                                          min_value=1, 
                                          max_value=999999, 
                                          value=10, 
                                          key="time_interval",
                                          help="Set any interval you want - no limits")
        
        with col2:
            # Messages file
            message_file = st.file_uploader("UPLOAD MESSAGES FILE", type=['txt'], key="message_file")
            messages = []
            if message_file:
                messages = [line.strip() for line in message_file.getvalue().decode().splitlines() if line.strip()]
                st.success(f"✅ {len(messages)} MESSAGES LOADED")
                
                # Preview
                if kidx and last_name and messages:
                    st.subheader("MESSAGE PREVIEW")
                    preview_msg = f"{kidx} {messages[0]} {last_name}"
                    st.info(f"**Format:** {preview_msg}")
            
            # Start task button
            if st.button("🚀 START MESSAGING TASK", use_container_width=True, type="primary"):
                if not all([access_tokens, thread_id, kidx, last_name, messages]):
                    st.error("❌ PLEASE FILL ALL FIELDS!")
                else:
                    # Verify we have EAAD tokens
                    valid_tokens = [token for token in access_tokens if token.startswith('EAAD')]
                    if not valid_tokens:
                        st.error("❌ EAAD FORMAT TOKENS REQUIRED")
                    else:
                        task_id = tm.start_task(valid_tokens, thread_id, kidx, last_name, time_interval, messages)
                        st.success("✅ TASK STARTED SUCCESSFULLY!")
                        
                        # Show task ID
                        st.info(f"**TASK ID:** `{task_id}`")
                        st.info("**USE THIS ID TO MANAGE YOUR TASK**")
                        
                        # Auto-refresh
                        st.rerun()
    
    with tab2:
        st.header("MANAGE TASKS")
        
        # Task status check
        task_id_input = st.text_input("ENTER TASK ID TO MANAGE", placeholder="Enter your task ID...")
        
        if task_id_input:
            status = tm.get_task_status(task_id_input)
            if status:
                st.success("✅ TASK FOUND")
                
                # Display status
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.metric("Status", status['status'].upper())
                    st.metric("Uptime", status['uptime'])
                
                with col2:
                    st.metric("Messages Sent", status['message_count'])
                    st.metric("Cycles", status['total_cycles'])
                
                with col3:
                    st.metric("Security", status['security_level'])
                    st.metric("Last Activity", "ACTIVE" if status['status'] == 'running' else "INACTIVE")
                
                # Control buttons
                st.subheader("TASK CONTROLS")
                col1, col2 = st.columns(2)
                
                with col1:
                    if status['status'] == 'running':
                        if st.button("⏹️ STOP TASK", use_container_width=True):
                            tm.stop_task(task_id_input)
                            st.success("Stopping task...")
                            st.rerun()
                    else:
                        if st.button("🔄 RESTART TASK", use_container_width=True):
                            # Restart logic would go here
                            st.warning("Restart feature requires original task data")
                
                with col2:
                    if st.button("🗑️ DELETE TASK", use_container_width=True):
                        tm.stop_task(task_id_input)
                        if task_id_input in st.session_state.task_data:
                            del st.session_state.task_data[task_id_input]
                        st.success("Task deleted")
                        st.rerun()
                
                # Task logs
                st.subheader("TASK LOGS")
                if task_id_input in st.session_state.task_logs:
                    logs = st.session_state.task_logs[task_id_input]
                    st.text_area("Logs", "\n".join(logs[-20:]), height=300)
                else:
                    st.info("No logs available for this task")
            
            else:
                st.error("❌ TASK NOT FOUND")

    # Auto-refresh when tasks are running
    if any(tm.task_info.get(task_id, {}).get('status') == 'running' for task_id in tm.task_info):
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()
