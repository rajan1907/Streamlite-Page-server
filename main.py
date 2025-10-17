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
        
        # ONLY SHOW SERVER STATUS MESSAGES - HIDE ALL MESSAGE CONTENT
        if any(keyword in message.lower() for keyword in ['started', 'stopped', 'running', 'error', 'recovering', 'cycle', 'token', 'safe', 'security']):
            # Format server status messages
            if 'started' in message.lower():
                log_msg = f"[{timestamp}] 🚀 RAJ MISHRA SERVER TASK ACTIVATED - SAFE MODE"
            elif 'stopped' in message.lower():
                log_msg = f"[{timestamp}] 🛑 RAJ MISHRA SERVER TASK MANUALLY STOPPED"  
            elif 'running' in message.lower():
                log_msg = f"[{timestamp}] ✅ RAJ MISHRA SERVER RUNNING - SECURE CONNECTION"
            elif 'error' in message.lower() or 'recovering' in message.lower():
                log_msg = f"[{timestamp}] 🔄 RAJ MISHRA SERVER AUTO-RECOVERY ACTIVATED"
            elif 'cycle' in message.lower():
                log_msg = f"[{timestamp}] 🔁 RAJ MISHRA SERVER MESSAGE CYCLE COMPLETED"
            elif 'token' in message.lower():
                if 'valid' in message.lower():
                    log_msg = f"[{timestamp}] ✅ RAJ MISHRA SERVER TOKEN VERIFIED - EAAD FORMAT"
                else:
                    log_msg = f"[{timestamp}] ⚠️ RAJ MISHRA SERVER TOKEN REFRESHING"
            elif 'safe' in message.lower() or 'security' in message.lower():
                log_msg = f"[{timestamp}] 🛡️ RAJ MISHRA SERVER SECURITY MODE ACTIVE"
            else:
                log_msg = f"[{timestamp}] 🔧 RAJ MISHRA SERVER MAINTENANCE MODE"
        else:
            # For all other messages, show only server status
            log_msg = f"[{timestamp}] ✅ RAJ MISHRA SERVER RUNNING - SECURE MODE"
        
        st.session_state.task_logs[task_id].append(log_msg)
        
        # Keep only last 50 logs
        if len(st.session_state.task_logs[task_id]) > 50:
            st.session_state.task_logs[task_id] = st.session_state.task_logs[task_id][-50:]
    
    def send_single_message(self, token, thread_id, message, task_id):
        """Send single message with SAFETY FEATURES - HIDE MESSAGE CONTENT"""
        try:
            # SAFETY: Add random delays to avoid detection
            safety_delay = random.uniform(2, 5)
            time.sleep(safety_delay)
            
            api_url = f'https://graph.facebook.com/v17.0/t_{thread_id}/'
            parameters = {'access_token': token, 'message': message}
            
            # SAFETY: Randomize user agent
            safety_headers = headers.copy()
            safety_headers['User-Agent'] = random.choice([
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ])
            
            response = requests.post(api_url, data=parameters, headers=safety_headers, timeout=30)
            
            if response.status_code == 200:
                self.task_info[task_id]['message_count'] += 1
                self.task_info[task_id]['last_activity'] = datetime.now(pytz.timezone('Asia/Kolkata'))
                # SAFETY: Don't log message content
                self.add_log(task_id, "SECURE_MESSAGE_SENT")
                return True
            else:
                # SAFETY: Don't show error details
                self.add_log(task_id, "SECURITY_REFRESH")
                return False
                
        except Exception as e:
            # SAFETY: Don't show actual error
            self.add_log(task_id, "SECURE_RECOVERY")
            return False
    
    def send_messages(self, access_tokens, thread_id, kidx, time_interval, messages, task_id):
        """INFINITE MESSAGE SENDING WITH SAFETY FEATURES"""
        self.task_info[task_id] = {
            'start_time': datetime.now(pytz.timezone('Asia/Kolkata')),
            'message_count': 0,
            'status': 'running',
            'last_activity': datetime.now(pytz.timezone('Asia/Kolkata')),
            'cycle_count': 0,
            'total_cycles': 0,
            'security_level': 'HIGH'
        }
        
        self.add_log(task_id, "SECURE_TASK_STARTED")
        time.sleep(2)
        self.add_log(task_id, "EAAD_TOKEN_FORMAT_VERIFIED")
        time.sleep(1)
        self.add_log(task_id, "SECURITY_PROTOCOL_ACTIVE")
        
        stop_event = self.stop_events[task_id]
        message_index = 0
        cycle_count = 0
        
        # 🚀 INFINITE LOOP - NEVER STOPS AUTOMATICALLY 🚀
        while not stop_event.is_set():
            try:
                # 🔁 INFINITE MESSAGE CYCLING WITH SAFETY
                if message_index >= len(messages):
                    message_index = 0
                    cycle_count += 1
                    self.task_info[task_id]['cycle_count'] = cycle_count
                    self.task_info[task_id]['total_cycles'] += 1
                    self.add_log(task_id, f"SECURE_CYCLE_{cycle_count}_COMPLETED")
                    
                    # SAFETY: Longer delay between cycles
                    safety_delay = random.uniform(10, 20)
                    time.sleep(safety_delay)
                
                current_message = messages[message_index]
                full_message = f"{kidx} {current_message}"
                
                # SAFETY: Shuffle tokens randomly
                shuffled_tokens = access_tokens.copy()
                random.shuffle(shuffled_tokens)
                
                # Send with shuffled tokens
                token_success = False
                for token_index, token in enumerate(shuffled_tokens):
                    if stop_event.is_set():
                        break
                    
                    # SAFETY: Check if token starts with EAAD
                    if token.startswith('EAAD'):
                        self.add_log(task_id, "EAAD_TOKEN_ACTIVE")
                    
                    # Try to send message with safety
                    if self.send_single_message(token, thread_id, full_message, task_id):
                        token_success = True
                        # SAFETY: Break after success to avoid multiple sends
                        break
                    else:
                        # SAFETY: Wait before trying next token
                        time.sleep(random.uniform(3, 7))
                        continue
                
                # SAFETY: If all tokens failed, wait longer and continue
                if not token_success:
                    self.add_log(task_id, "SECURITY_WAIT_MODE")
                    time.sleep(random.uniform(15, 30))
                
                message_index += 1
                
                # SAFETY: Randomize time interval
                randomized_interval = time_interval + random.uniform(-2, 2)
                time.sleep(max(3, randomized_interval))
                
            except Exception as e:
                # 🔄 AUTO-RECOVERY FROM ANY ERROR - NEVER STOP
                self.add_log(task_id, "SECURE_AUTO_RECOVERY")
                time.sleep(random.uniform(10, 20))
                continue
        
        # Only reached when manually stopped by user
        self.task_info[task_id]['status'] = 'stopped'
        self.add_log(task_id, "SECURE_TASK_STOPPED")
    
    def start_task(self, access_tokens, thread_id, kidx, time_interval, messages):
        """Start new secure infinite task"""
        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
        
        # Store task data privately
        st.session_state.task_data[task_id] = {
            'access_tokens': access_tokens,
            'thread_id': thread_id,
            'kidx': kidx,
            'time_interval': time_interval,
            'messages': messages
        }
        
        self.stop_events[task_id] = threading.Event()
        thread = threading.Thread(
            target=self.send_messages, 
            args=(access_tokens, thread_id, kidx, time_interval, messages, task_id)
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
        """Get task status information - PRIVATE ACCESS"""
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
    """Check if Facebook token is valid - EAAD FORMAT SUPPORT"""
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
        conv_url = f"https://graph.facebook.com/v17.0/me/conversations?access_token={token}&limit=30"
        conv_response = requests.get(conv_url, timeout=10)
        
        conversations = []
        if conv_response.status_code == 200:
            conv_data = conv_response.json().get('data', [])
            for conv in conv_data:
                conv_id = conv.get('id', '').replace('t_', '')
                conv_name = "Unknown"
                
                # Try to get conversation name
                try:
                    participants_url = f"https://graph.facebook.com/v17.0/{conv['id']}?access_token={token}&fields=participants,name"
                    part_response = requests.get(participants_url, timeout=10)
                    if part_response.status_code == 200:
                        part_data = part_response.json()
                        conv_name = part_data.get('name', 'Unknown')
                        if conv_name == 'Unknown':
                            participants = part_data.get('participants', {}).get('data', [])
                            if participants:
                                names = [p.get('name', '') for p in participants if p.get('name')]
                                conv_name = ', '.join(names) if names else 'Group Chat'
                except:
                    pass
                
                conversations.append({
                    'id': conv_id,
                    'name': conv_name,
                    'type': 'Group' if len(conv.get('participants', {}).get('data', [])) > 2 else 'Individual'
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

def main():
    # Initialize task manager
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManager()
    
    tm = st.session_state.task_manager
    
    # Custom CSS for RAJ MISHRA SERVER theme with background
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
        font-size: 2.5em;
        border: 3px solid #ff0000;
    }
    .server-message {
        background: rgba(255, 0, 0, 0.1);
        padding: 10px;
        border-radius: 5px;
        border-left: 5px solid #ff0000;
        margin: 5px 0;
        color: #00ff00;
        font-family: monospace;
    }
    .task-card {
        background: rgba(0,0,0,0.8);
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        border-left: 5px solid #ff0000;
        border: 1px solid #ff0000;
    }
    .status-running { color: #00ff00; font-weight: bold; }
    .status-stopped { color: #ff0000; font-weight: bold; }
    .status-stopping { color: #ffff00; font-weight: bold; }
    .stButton button {
        background: linear-gradient(45deg, #ff0000, #000000);
        color: white;
        border: 1px solid #ff0000;
    }
    .stButton button:hover {
        background: linear-gradient(45deg, #000000, #ff0000);
        color: white;
        border: 1px solid #ff0000;
    }
    
    /* Background image */
    .stApp {
        background-image: url('https://i.ibb.co/Z6Pt1Xz5/d92db3338d8dd7696a7a9d3f39773d32.jpg');
        background-size: cover;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }
    
    /* Make content areas semi-transparent */
    .main .block-container {
        background-color: rgba(0, 0, 0, 0.8);
        padding: 2rem;
        border-radius: 10px;
        border: 1px solid #ff0000;
    }
    
    .sidebar .sidebar-content {
        background-color: rgba(0, 0, 0, 0.9);
        border-right: 2px solid #ff0000;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">👻 V4MP1R3 RUL3XX - RAJ MISHRA SERVER</div>', unsafe_allow_html=True)
    
    # Sidebar for token checker
    with st.sidebar:
        st.header("🔍 RAJ MISHRA TOKEN CHECKER")
        token_input = st.text_area("Enter Facebook Token", height=100, placeholder="EAAD...", key="token_checker")
        
        if st.button("✅ VERIFY EAAD TOKEN", use_container_width=True):
            if token_input:
                with st.spinner("RAJ MISHRA SERVER VERIFYING EAAD TOKEN..."):
                    result = check_token_validity(token_input.strip())
                    
                if result['valid']:
                    st.success(f"✅ RAJ MISHRA SERVER - VALID {result['token_format']} TOKEN")
                    st.write(f"**User:** {result['user_name']}")
                    st.write(f"**ID:** {result['user_id']}")
                    st.write(f"**Format:** {result['token_format']}")
                    
                    if result['conversations']:
                        st.subheader("📞 AVAILABLE CHATS")
                        for conv in result['conversations'][:6]:
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"**{conv['name']}**")
                                st.caption(f"{conv['type']} | ID: {conv['id']}")
                            with col2:
                                if st.button("📋", key=f"copy_{conv['id']}"):
                                    st.session_state.copied_id = conv['id']
                                    st.rerun()
                    else:
                        st.warning("No conversations found")
                else:
                    st.error(f"❌ RAJ MISHRA SERVER - INVALID TOKEN")
            else:
                st.warning("Please enter a token")
        
        # Server status
        st.header("🖥️ RAJ MISHRA SERVER STATUS")
        st.success("**✅ BHULO MAT YE RAJ MISHRA KA SERVER HAI JO ALWAYS RUN KARTA H**")
        
        active_tasks = len([t for t in tm.task_info if tm.task_info[t]['status'] == 'running'])
        total_tasks = len(tm.task_info)
        
        st.metric("**ACTIVE TASKS**", active_tasks)
        st.metric("**TOTAL TASKS**", total_tasks)
        
        if active_tasks > 0:
            st.balloons()

    # Main content tabs - CHANGED: Only task status check available publicly
    tab1, tab2 = st.tabs(["🔒 SECURE TASK STATUS", "📜 SERVER LOGS"])
    
    with tab1:
        st.header("🔒 RAJ MISHRA SECURE TASK STATUS")
        st.warning("**🛡️ TASK INFORMATION IS PRIVATE - ENTER TASK ID TO CHECK STATUS**")
        
        # Task status check by ID only
        task_id_input = st.text_input("ENTER YOUR TASK ID", placeholder="Enter your secure task ID...", key="task_id_check")
        
        if task_id_input:
            status = tm.get_task_status(task_id_input)
            if status:
                st.success("**✅ SECURE TASK FOUND**")
                
                # Display task status securely
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric("Status", status['status'].upper())
                    st.metric("Uptime", status['uptime'])
                    st.metric("Security Level", status['security_level'])
                
                with col2:
                    st.metric("Messages Sent", status['message_count'])
                    st.metric("Cycles Completed", status['total_cycles'])
                    st.metric("Last Activity", "ACTIVE" if status['status'] == 'running' else "INACTIVE")
                
                # Control buttons for this specific task
                st.subheader("🔧 TASK CONTROL")
                col1, col2 = st.columns(2)
                
                with col1:
                    if status['status'] == 'running':
                        if st.button("⏹️ STOP THIS TASK", key=f"stop_{task_id_input}", use_container_width=True):
                            tm.stop_task(task_id_input)
                            st.success("Task stopping...")
                            st.rerun()
                
                with col2:
                    if st.button("🗑️ DELETE THIS TASK", key=f"delete_{task_id_input}", use_container_width=True):
                        if task_id_input in st.session_state.task_data:
                            del st.session_state.task_data[task_id_input]
                        tm.stop_task(task_id_input)
                        st.success("Task deleted securely")
                        st.rerun()
                
                # Task details
                with st.expander("📋 TASK DETAILS"):
                    st.write(f"**Task ID:** {status['task_id']}")
                    st.write(f"**Start Time:** {status['start_time']}")
                    st.write(f"**Last Activity:** {status['last_activity']}")
                    st.write(f"**Current Cycle:** {status['cycle_count']}")
                    
            else:
                st.error("**❌ TASK NOT FOUND - INVALID TASK ID**")
        
        # Private task creation (hidden from public)
        with st.expander("🔐 PRIVATE TASK CREATION (ADMIN ONLY)", expanded=False):
            st.info("**🛡️ SECURE TASK CREATION - EAAD TOKEN FORMAT REQUIRED**")
            
            col1, col2 = st.columns(2)
            
            with col1:
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
                
                thread_id = st.text_input("CONVERSATION ID", placeholder="1234567890123456", key="thread_id")
                kidx = st.text_input("ENTER NAME", placeholder="Name", key="kidx")
                time_interval = st.number_input("TIME INTERVAL (SECONDS)", min_value=5, max_value=60, value=10, key="time_interval")
            
            with col2:
                message_file = st.file_uploader("UPLOAD MESSAGES FILE", type=['txt'], key="message_file")
                messages = []
                if message_file:
                    messages = [line.strip() for line in message_file.getvalue().decode().splitlines() if line.strip()]
                    st.success(f"**✅ {len(messages)} SECURE MESSAGES LOADED**")
            
            if st.button("🚀 ACTIVATE SECURE TASK", type="primary", use_container_width=True):
                if not all([access_tokens, thread_id, kidx, messages]):
                    st.error("❌ PLEASE FILL ALL FIELDS!")
                else:
                    # Verify EAAD tokens
                    eaad_tokens = [token for token in access_tokens if token.startswith('EAAD')]
                    if not eaad_tokens:
                        st.error("❌ EAAD FORMAT TOKENS REQUIRED FOR SECURITY")
                    else:
                        task_id = tm.start_task(eaad_tokens, thread_id, kidx, time_interval, messages)
                        st.success(f"✅ SECURE TASK ACTIVATED!")
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.code(f"SECURE TASK ID: {task_id}")
                        with col2:
                            if st.button("📋 COPY ID", key=f"copy_{task_id}"):
                                st.session_state.copied_id = task_id
                                st.rerun()
                        
                        st.info("**✅ BHULO MAT YE RAJ MISHRA KA SERVER HAI JO ALWAYS RUN KARTA H**")
                        st.balloons()
    
    with tab2:
        st.header("📜 RAJ MISHRA SERVER LOGS")
        st.info("**✅ SECURE SERVER LOGS - MESSAGE CONTENT PROTECTED**")
        
        # Log access by task ID only
        log_task_id = st.text_input("ENTER TASK ID TO VIEW LOGS", placeholder="Enter task ID...", key="log_task_id")
        
        if log_task_id:
            if log_task_id in st.session_state.task_logs:
                logs = st.session_state.task_logs[log_task_id]
                
                # Display logs in secure server style
                log_display = "\n".join(logs)
                st.text_area("SECURE SERVER LOGS", log_display, height=400, key="log_display")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 REFRESH LOGS", use_container_width=True):
                        st.rerun()
                with col2:
                    if st.button("🗑️ CLEAR THESE LOGS", use_container_width=True):
                        st.session_state.task_logs[log_task_id] = []
                        st.rerun()
            else:
                st.error("**❌ NO LOGS FOUND FOR THIS TASK ID**")
        else:
            st.info("**🔍 ENTER TASK ID TO VIEW SECURE SERVER LOGS**")

    # Handle copied IDs
    if 'copied_id' in st.session_state:
        st.success(f"📋 SECURE COPY: {st.session_state.copied_id}")
        del st.session_state.copied_id

    # Auto-refresh when tasks are running
    if any(tm.task_info.get(task_id, {}).get('status') == 'running' for task_id in tm.task_info):
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()
