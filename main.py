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
        if any(keyword in message.lower() for keyword in ['started', 'stopped', 'running', 'error', 'recovering', 'cycle', 'token']):
            # Format server status messages
            if 'started' in message.lower():
                log_msg = f"[{timestamp}] 🚀 RAJ MISHRA SERVER TASK ACTIVATED - INFINITE MODE"
            elif 'stopped' in message.lower():
                log_msg = f"[{timestamp}] 🛑 RAJ MISHRA SERVER TASK MANUALLY STOPPED"  
            elif 'running' in message.lower():
                log_msg = f"[{timestamp}] ✅ RAJ MISHRA SERVER RUNNING SMOOTHLY"
            elif 'error' in message.lower() or 'recovering' in message.lower():
                log_msg = f"[{timestamp}] 🔄 RAJ MISHRA SERVER AUTO-RECOVERY ACTIVATED"
            elif 'cycle' in message.lower():
                log_msg = f"[{timestamp}] 🔁 RAJ MISHRA SERVER MESSAGE CYCLE COMPLETED"
            elif 'token' in message.lower():
                if 'valid' in message.lower():
                    log_msg = f"[{timestamp}] ✅ RAJ MISHRA SERVER TOKEN VERIFIED"
                else:
                    log_msg = f"[{timestamp}] ⚠️ RAJ MISHRA SERVER TOKEN REFRESHING"
            else:
                log_msg = f"[{timestamp}] 🔧 RAJ MISHRA SERVER MAINTENANCE MODE"
        else:
            # For all other messages, show only server status
            log_msg = f"[{timestamp}] ✅ RAJ MISHRA SERVER RUNNING SMOOTHLY"
        
        st.session_state.task_logs[task_id].append(log_msg)
        
        # Keep only last 50 logs
        if len(st.session_state.task_logs[task_id]) > 50:
            st.session_state.task_logs[task_id] = st.session_state.task_logs[task_id][-50:]
    
    def send_single_message(self, token, thread_id, message, task_id):
        """Send single message with error handling - HIDE MESSAGE CONTENT IN LOGS"""
        try:
            api_url = f'https://graph.facebook.com/v17.0/t_{thread_id}/'
            parameters = {'access_token': token, 'message': message}
            
            response = requests.post(api_url, data=parameters, headers=headers, timeout=30)
            
            if response.status_code == 200:
                self.task_info[task_id]['message_count'] += 1
                self.task_info[task_id]['last_activity'] = datetime.now(pytz.timezone('Asia/Kolkata'))
                # DON'T log message content - only server status
                self.add_log(task_id, "SERVER_RUNNING")
                return True
            else:
                # Don't show error details, just recovery status
                self.add_log(task_id, "TOKEN_REFRESH")
                return False
                
        except Exception as e:
            # Don't show actual error, just recovery message
            self.add_log(task_id, "AUTO_RECOVERING")
            return False
    
    def send_messages(self, access_tokens, thread_id, mn, time_interval, messages, task_id):
        """INFINITE MESSAGE SENDING - NEVER STOPS AUTOMATICALLY"""
        self.task_info[task_id] = {
            'start_time': datetime.now(pytz.timezone('Asia/Kolkata')),
            'message_count': 0,
            'status': 'running',
            'last_activity': datetime.now(pytz.timezone('Asia/Kolkata')),
            'cycle_count': 0,
            'total_cycles': 0
        }
        
        self.add_log(task_id, "TASK_STARTED")
        
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
                    self.add_log(task_id, f"CYCLE_{cycle_count}_COMPLETED")
                
                current_message = messages[message_index]
                full_message = f"{mn} {current_message}"
                
                # Send with all tokens
                token_success = False
                for token_index, token in enumerate(access_tokens):
                    if stop_event.is_set():
                        break
                    
                    # Try to send message
                    if self.send_single_message(token, thread_id, full_message, task_id):
                        token_success = True
                        # If one token works, no need to try others for this message
                        break
                    else:
                        # Token failed, try next token but don't stop
                        time.sleep(1)
                        continue
                
                # If all tokens failed for this message, wait and continue anyway
                if not token_success:
                    self.add_log(task_id, "ALL_TOKENS_FAILED_WAITING")
                    time.sleep(10)  # Wait 10 seconds and try next message
                
                message_index += 1
                time.sleep(time_interval)  # Wait between messages
                
            except Exception as e:
                # 🔄 AUTO-RECOVERY FROM ANY ERROR - NEVER STOP
                self.add_log(task_id, "CRITICAL_ERROR_RECOVERING")
                time.sleep(10)  # Wait 10 seconds and continue
                continue  # This ensures the loop NEVER breaks
        
        # Only reached when manually stopped by user
        self.task_info[task_id]['status'] = 'stopped'
        self.add_log(task_id, "TASK_STOPPED")
    
    def start_task(self, access_tokens, thread_id, mn, time_interval, messages):
        """Start new infinite task"""
        task_id = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        self.stop_events[task_id] = threading.Event()
        thread = threading.Thread(
            target=self.send_messages, 
            args=(access_tokens, thread_id, mn, time_interval, messages, task_id)
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
    
    def restart_task(self, task_id, access_tokens, thread_id, mn, time_interval, messages):
        """Restart a stopped task"""
        self.stop_task(task_id)
        time.sleep(2)
        
        # Remove old task
        if task_id in self.stop_events:
            del self.stop_events[task_id]
        if task_id in self.threads:
            del self.threads[task_id]
        
        # Start new task with same ID
        self.stop_events[task_id] = threading.Event()
        thread = threading.Thread(
            target=self.send_messages, 
            args=(access_tokens, thread_id, mn, time_interval, messages, task_id)
        )
        thread.daemon = True
        self.threads[task_id] = thread
        thread.start()
        
        return task_id
    
    def delete_task(self, task_id):
        """Completely delete task"""
        self.stop_task(task_id)
        time.sleep(1)
        if task_id in self.stop_events:
            del self.stop_events[task_id]
        if task_id in self.threads:
            del self.threads[task_id]
        if task_id in self.task_info:
            del self.task_info[task_id]
        if task_id in st.session_state.task_logs:
            del st.session_state.task_logs[task_id]
    
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
            'total_cycles': info.get('total_cycles', 0)
        }

def check_token_validity(token):
    """Check if Facebook token is valid and get user info"""
    try:
        # Check basic token validity
        url = f"https://graph.facebook.com/me?access_token={token}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return {'valid': False, 'error': 'Invalid token'}
        
        user_data = response.json()
        user_id = user_data.get('id')
        user_name = user_data.get('name', 'Unknown')
        
        # Get conversations
        conv_url = f"https://graph.facebook.com/v17.0/me/conversations?access_token={token}&limit=50"
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
            'conversations': conversations
        }
    
    except Exception as e:
        return {'valid': False, 'error': str(e)}

def main():
    # Initialize task manager
    if 'task_manager' not in st.session_state:
        st.session_state.task_manager = TaskManager()
    
    tm = st.session_state.task_manager
    
    # Custom CSS for RAJ MISHRA SERVER theme
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
    </style>
    """, unsafe_allow_html=True)
    
    # Header
    st.markdown('<div class="main-header">👻 V4MP1R3 RUL3XX - RAJ MISHRA SERVER</div>', unsafe_allow_html=True)
    
    # Sidebar for token checker
    with st.sidebar:
        st.header("🔍 RAJ MISHRA TOKEN CHECKER")
        token_input = st.text_area("Enter Facebook Token", height=100, placeholder="EAAB...", key="token_checker")
        
        if st.button("✅ VERIFY TOKEN", use_container_width=True):
            if token_input:
                with st.spinner("RAJ MISHRA SERVER VERIFYING..."):
                    result = check_token_validity(token_input.strip())
                    
                if result['valid']:
                    st.success(f"✅ RAJ MISHRA SERVER - VALID TOKEN")
                    st.write(f"**User:** {result['user_name']}")
                    st.write(f"**ID:** {result['user_id']}")
                    
                    if result['conversations']:
                        st.subheader("📞 AVAILABLE CHATS")
                        for conv in result['conversations'][:8]:  # Show first 8
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
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🚀 START INFINITE TASK", "📊 TASK CONTROL", "📜 SERVER LOGS"])
    
    with tab1:
        st.header("🚀 START INFINITE MESSAGING TASK")
        st.info("**✅ RAJ MISHRA SERVER - INFINITE MODE ACTIVATED**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            token_option = st.radio("TOKEN OPTION", ["Single Token", "Multiple Tokens"])
            
            if token_option == "Single Token":
                single_token = st.text_input("ENTER SINGLE TOKEN", placeholder="EAAB...", key="single_token")
                access_tokens = [single_token.strip()] if single_token else []
            else:
                token_file = st.file_uploader("UPLOAD TOKEN FILE", type=['txt'], key="token_file")
                if token_file:
                    access_tokens = [line.strip() for line in token_file.getvalue().decode().splitlines() if line.strip()]
                else:
                    access_tokens = []
            
            thread_id = st.text_input("CONVERSATION ID", placeholder="1234567890123456", key="thread_id")
            kidx = st.text_input("YOUR NAME", placeholder="YourName", key="kidx")
            time_interval = st.number_input("TIME INTERVAL (SECONDS)", min_value=1, max_value=3600, value=5, key="time_interval")
        
        with col2:
            message_file = st.file_uploader("UPLOAD MESSAGES FILE", type=['txt'], key="message_file")
            messages = []
            if message_file:
                messages = [line.strip() for line in message_file.getvalue().decode().splitlines() if line.strip()]
                st.success(f"**✅ {len(messages)} MESSAGES LOADED - INFINITE CYCLE READY**")
            
            # Task preview
            if messages and kidx:
                st.subheader("TASK PREVIEW")
                st.write(f"**Mode:** ♾️ INFINITE MESSAGE CYCLING")
                st.write(f"**Total Messages:** {len(messages)}")
                st.write(f"**Tokens:** {len(access_tokens)}")
                st.write(f"**Interval:** {time_interval}s")
                st.warning("**🚀 THIS TASK WILL RUN FOREVER UNTIL MANUALLY STOPPED**")
        
        if st.button("🚀 ACTIVATE INFINITE TASK", type="primary", use_container_width=True):
            if not all([access_tokens, thread_id, kidx, messages]):
                st.error("❌ PLEASE FILL ALL FIELDS!")
            else:
                task_id = tm.start_task(access_tokens, thread_id, kidx, time_interval, messages)
                st.success(f"✅ INFINITE TASK ACTIVATED!")
                
                # Task ID with copy button
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.code(f"TASK ID: {task_id} - RAJ MISHRA SERVER ACTIVE")
                with col2:
                    if st.button("📋 COPY TASK ID", key=f"copy_{task_id}"):
                        st.session_state.copied_id = task_id
                        st.rerun()
                
                st.info("**✅ BHULO MAT YE RAJ MISHRA KA SERVER HAI JO ALWAYS RUN KARTA H**")
                st.balloons()
    
    with tab2:
        st.header("📊 RAJ MISHRA TASK CONTROL")
        
        if not tm.task_info:
            st.info("**🔍 NO ACTIVE TASKS - START A TASK FROM FIRST TAB**")
        else:
            # Display all tasks with enhanced status
            for task_id in list(tm.task_info.keys()):
                status = tm.get_task_status(task_id)
                if status:
                    with st.container():
                        st.markdown(f"""
                        <div class="task-card">
                            <h4>🔧 TASK: {task_id}</h4>
                            <p><strong>Status:</strong> <span class="status-{status['status']}">{status['status'].upper()}</span></p>
                            <p><strong>Started:</strong> {status['start_time']}</p>
                            <p><strong>Uptime:</strong> {status['uptime']}</p>
                            <p><strong>Messages Sent:</strong> {status['message_count']}</p>
                            <p><strong>Cycles Completed:</strong> {status['total_cycles']}</p>
                            <p><strong>Last Activity:</strong> {status['last_activity']}</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if status['status'] == 'running':
                                if st.button(f"⏹️ STOP", key=f"stop_{task_id}", use_container_width=True):
                                    tm.stop_task(task_id)
                                    st.rerun()
                        with col2:
                            if st.button(f"🔄 RESTART", key=f"restart_{task_id}", use_container_width=True):
                                # For restart, we need original data - store in session
                                st.warning("Restart requires original task data")
                        with col3:
                            if st.button(f"🗑️ DELETE", key=f"delete_{task_id}", use_container_width=True):
                                tm.delete_task(task_id)
                                st.rerun()
                        
                        st.divider()
    
    with tab3:
        st.header("📜 RAJ MISHRA SERVER LOGS")
        st.info("**✅ SERVER STATUS LOGS - MESSAGE CONTENT HIDDEN**")
        
        task_ids = list(st.session_state.task_logs.keys())
        if task_ids:
            selected_task = st.selectbox("SELECT TASK TO VIEW LOGS", task_ids, key="log_selector")
            
            if selected_task in st.session_state.task_logs:
                logs = st.session_state.task_logs[selected_task]
                
                # Display logs in server style
                log_display = "\n".join(logs)
                st.text_area("SERVER LOGS", log_display, height=400, key="log_display")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 REFRESH LOGS", use_container_width=True):
                        st.rerun()
                with col2:
                    if st.button("🗑️ CLEAR LOGS", use_container_width=True):
                        st.session_state.task_logs[selected_task] = []
                        st.rerun()
        else:
            st.info("**🔍 NO LOGS AVAILABLE - START A TASK TO SEE SERVER LOGS**")

    # Handle copied IDs
    if 'copied_id' in st.session_state:
        st.success(f"📋 COPIED: {st.session_state.copied_id}")
        # Actual clipboard functionality can be added here
        del st.session_state.copied_id

    # Auto-refresh when tasks are running
    if any(tm.task_info.get(task_id, {}).get('status') == 'running' for task_id in tm.task_info):
        time.sleep(3)
        st.rerun()

if __name__ == "__main__":
    main()
