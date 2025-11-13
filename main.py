import streamlit as st
import time
import threading
import uuid
import hashlib
import os
import json
import urllib.parse
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
import requests
import sqlite3
from datetime import datetime
import base64

# Page configuration
st.set_page_config(
    page_title="Facebook Messenger Automation",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Database setup
def init_db():
    conn = sqlite3.connect('automation.db')
    c = conn.cursor()
    
    # Users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # User config table
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_config (
            user_id INTEGER PRIMARY KEY,
            chat_id TEXT,
            name_prefix TEXT,
            delay INTEGER DEFAULT 30,
            cookies TEXT,
            messages TEXT,
            automation_running BOOLEAN DEFAULT FALSE,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # Admin E2EE threads table
    c.execute('''
        CREATE TABLE IF NOT EXISTS admin_threads (
            user_id INTEGER PRIMARY KEY,
            thread_id TEXT,
            cookies TEXT,
            chat_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# Initialize database
init_db()

# Database functions
def create_user(username, password):
    try:
        conn = sqlite3.connect('automation.db')
        c = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute('INSERT INTO users (username, password_hash) VALUES (?, ?)', 
                 (username, password_hash))
        user_id = c.lastrowid
        
        # Create default config
        c.execute('''
            INSERT INTO user_config (user_id, chat_id, name_prefix, delay, cookies, messages, automation_running)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, '', '', 30, '', 'Hello!\nHow are you?', False))
        
        conn.commit()
        conn.close()
        return True, user_id
    except Exception as e:
        return False, str(e)

def verify_user(username, password):
    try:
        conn = sqlite3.connect('automation.db')
        c = conn.cursor()
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        c.execute('SELECT id FROM users WHERE username = ? AND password_hash = ?', 
                 (username, password_hash))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

def get_user_config(user_id):
    try:
        conn = sqlite3.connect('automation.db')
        c = conn.cursor()
        c.execute('SELECT * FROM user_config WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        
        if result:
            return {
                'chat_id': result[1],
                'name_prefix': result[2],
                'delay': result[3],
                'cookies': result[4],
                'messages': result[5],
                'automation_running': bool(result[6])
            }
        return None
    except:
        return None

def update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
    try:
        conn = sqlite3.connect('automation.db')
        c = conn.cursor()
        c.execute('''
            UPDATE user_config 
            SET chat_id = ?, name_prefix = ?, delay = ?, cookies = ?, messages = ?
            WHERE user_id = ?
        ''', (chat_id, name_prefix, delay, cookies, messages, user_id))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def set_automation_running(user_id, running):
    try:
        conn = sqlite3.connect('automation.db')
        c = conn.cursor()
        c.execute('UPDATE user_config SET automation_running = ? WHERE user_id = ?', 
                 (running, user_id))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_automation_running(user_id):
    try:
        conn = sqlite3.connect('automation.db')
        c = conn.cursor()
        c.execute('SELECT automation_running FROM user_config WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return bool(result[0]) if result else False
    except:
        return False

def get_username(user_id):
    try:
        conn = sqlite3.connect('automation.db')
        c = conn.cursor()
        c.execute('SELECT username FROM users WHERE id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

def set_admin_e2ee_thread_id(user_id, thread_id, cookies, chat_type):
    try:
        conn = sqlite3.connect('automation.db')
        c = conn.cursor()
        c.execute('''
            INSERT OR REPLACE INTO admin_threads (user_id, thread_id, cookies, chat_type)
            VALUES (?, ?, ?, ?)
        ''', (user_id, thread_id, cookies, chat_type))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def get_admin_e2ee_thread_id(user_id):
    try:
        conn = sqlite3.connect('automation.db')
        c = conn.cursor()
        c.execute('SELECT thread_id FROM admin_threads WHERE user_id = ?', (user_id,))
        result = c.fetchone()
        conn.close()
        return result[0] if result else None
    except:
        return None

# Automation classes
class AutomationState:
    def __init__(self):
        self.running = False
        self.message_count = 0
        self.logs = []
        self.message_rotation_index = 0

# Session state initialization
if 'automation_states' not in st.session_state:
    st.session_state.automation_states = {}

if 'user_id' not in st.session_state:
    st.session_state.user_id = None

if 'username' not in st.session_state:
    st.session_state.username = None

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Initialize RAJ MISHRA user
def initialize_raj_mishra():
    try:
        user_id = verify_user("RAJ MISHRA", "raj123")
        if not user_id:
            success, user_id = create_user("RAJ MISHRA", "raj123")
            if success:
                st.success("RAJ MISHRA user created successfully!")
        return user_id
    except:
        return None

# Automation functions
def log_message(msg, automation_state=None, user_id=None):
    timestamp = time.strftime("%H:%M:%S")
    formatted_msg = f"[{timestamp}] {msg}"
    
    if automation_state:
        automation_state.logs.append(formatted_msg)
    elif user_id and user_id in st.session_state.automation_states:
        st.session_state.automation_states[user_id].logs.append(formatted_msg)

def setup_browser(automation_state=None, user_id=None):
    log_message('Setting up Chrome browser...', automation_state, user_id)
    
    chrome_options = Options()
    chrome_options.add_argument('--headless=new')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-setuid-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36')
    
    # For Streamlit Cloud
    chrome_options.binary_location = "/usr/bin/chromium-browser"
    
    try:
        service = Service(executable_path="/usr/bin/chromedriver")
        driver = webdriver.Chrome(service=service, options=chrome_options)
        log_message('Chrome started successfully!', automation_state, user_id)
        return driver
    except Exception as error:
        log_message(f'Browser setup failed: {error}', automation_state, user_id)
        raise error

def find_message_input(driver, process_id, automation_state=None, user_id=None):
    log_message(f'{process_id}: Finding message input...', automation_state, user_id)
    time.sleep(5)
    
    message_input_selectors = [
        'div[contenteditable="true"][role="textbox"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label*="message" i][contenteditable="true"]',
        'div[contenteditable="true"][spellcheck="true"]',
        '[role="textbox"][contenteditable="true"]',
        'textarea[placeholder*="message" i]',
        'div[aria-placeholder*="message" i]',
        '[contenteditable="true"]',
        'textarea',
        'input[type="text"]'
    ]
    
    for selector in message_input_selectors:
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            for element in elements:
                try:
                    is_editable = driver.execute_script("""
                        return arguments[0].contentEditable === 'true' || 
                               arguments[0].tagName === 'TEXTAREA' || 
                               arguments[0].tagName === 'INPUT';
                    """, element)
                    
                    if is_editable:
                        log_message(f'{process_id}: Found editable element', automation_state, user_id)
                        return element
                except:
                    continue
        except:
            continue
    
    return None

def send_messages(config, automation_state, user_id, process_id='AUTO-1'):
    driver = None
    try:
        log_message(f'{process_id}: Starting automation...', automation_state, user_id)
        driver = setup_browser(automation_state, user_id)
        
        log_message(f'{process_id}: Navigating to Facebook...', automation_state, user_id)
        driver.get('https://www.facebook.com/')
        time.sleep(8)
        
        if config['cookies'] and config['cookies'].strip():
            log_message(f'{process_id}: Adding cookies...', automation_state, user_id)
            cookie_array = config['cookies'].split(';')
            for cookie in cookie_array:
                cookie_trimmed = cookie.strip()
                if cookie_trimmed:
                    first_equal_index = cookie_trimmed.find('=')
                    if first_equal_index > 0:
                        name = cookie_trimmed[:first_equal_index].strip()
                        value = cookie_trimmed[first_equal_index + 1:].strip()
                        try:
                            driver.add_cookie({
                                'name': name,
                                'value': value,
                                'domain': '.facebook.com',
                                'path': '/'
                            })
                        except:
                            pass
        
        if config['chat_id']:
            chat_id = config['chat_id'].strip()
            log_message(f'{process_id}: Opening conversation {chat_id}...', automation_state, user_id)
            driver.get(f'https://www.facebook.com/messages/t/{chat_id}')
        else:
            log_message(f'{process_id}: Opening messages...', automation_state, user_id)
            driver.get('https://www.facebook.com/messages')
        
        time.sleep(10)
        
        message_input = find_message_input(driver, process_id, automation_state, user_id)
        
        if not message_input:
            log_message(f'{process_id}: Message input not found!', automation_state, user_id)
            automation_state.running = False
            set_automation_running(user_id, False)
            return 0
        
        delay = int(config['delay'])
        messages_sent = 0
        messages_list = [msg.strip() for msg in config['messages'].split('\n') if msg.strip()]
        
        if not messages_list:
            messages_list = ['Hello!']
        
        while automation_state.running:
            message_index = automation_state.message_rotation_index % len(messages_list)
            base_message = messages_list[message_index]
            automation_state.message_rotation_index += 1
            
            if config['name_prefix']:
                message_to_send = f"{config['name_prefix']} {base_message}"
            else:
                message_to_send = base_message
            
            try:
                driver.execute_script("""
                    const element = arguments[0];
                    const message = arguments[1];
                    
                    element.focus();
                    element.click();
                    
                    if (element.tagName === 'DIV') {
                        element.textContent = message;
                    } else {
                        element.value = message;
                    }
                    
                    element.dispatchEvent(new Event('input', { bubbles: true }));
                """, message_input, message_to_send)
                
                time.sleep(1)
                
                # Try to send using Enter key
                driver.execute_script("""
                    const element = arguments[0];
                    element.focus();
                    
                    const event = new KeyboardEvent('keydown', { 
                        key: 'Enter', 
                        code: 'Enter', 
                        keyCode: 13, 
                        which: 13, 
                        bubbles: true 
                    });
                    element.dispatchEvent(event);
                """, message_input)
                
                log_message(f'{process_id}: Sent: "{message_to_send[:30]}..."', automation_state, user_id)
                messages_sent += 1
                automation_state.message_count = messages_sent
                
                time.sleep(delay)
                
            except Exception as e:
                log_message(f'{process_id}: Send error: {str(e)[:100]}', automation_state, user_id)
                time.sleep(5)
        
        log_message(f'{process_id}: Automation stopped. Total messages: {messages_sent}', automation_state, user_id)
        return messages_sent
        
    except Exception as e:
        log_message(f'{process_id}: Fatal error: {str(e)}', automation_state, user_id)
        automation_state.running = False
        set_automation_running(user_id, False)
        return 0
    finally:
        if driver:
            try:
                driver.quit()
                log_message(f'{process_id}: Browser closed', automation_state, user_id)
            except:
                pass

def start_automation(user_config, user_id):
    if user_id not in st.session_state.automation_states:
        st.session_state.automation_states[user_id] = AutomationState()
    
    automation_state = st.session_state.automation_states[user_id]
    
    if automation_state.running:
        return
    
    automation_state.running = True
    automation_state.message_count = 0
    automation_state.logs = []
    automation_state.message_rotation_index = 0
    
    set_automation_running(user_id, True)
    
    thread = threading.Thread(target=send_messages, args=(user_config, automation_state, user_id))
    thread.daemon = True
    thread.start()

def stop_automation(user_id):
    if user_id in st.session_state.automation_states:
        st.session_state.automation_states[user_id].running = False
    set_automation_running(user_id, False)

# Streamlit UI Components
def login_page():
    st.title("🤖 Facebook Messenger Automation")
    st.markdown("---")
    
    # Auto-login RAJ MISHRA
    if st.button("Auto Login as RAJ MISHRA"):
        user_id = verify_user("RAJ MISHRA", "raj123")
        if user_id:
            st.session_state.user_id = user_id
            st.session_state.username = "RAJ MISHRA"
            st.session_state.logged_in = True
            st.rerun()
        else:
            st.error("RAJ MISHRA user not found!")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login")
            
            if login_btn:
                if username and password:
                    user_id = verify_user(username, password)
                    if user_id:
                        st.session_state.user_id = user_id
                        st.session_state.username = username
                        st.session_state.logged_in = True
                        st.rerun()
                    else:
                        st.error("Invalid username or password!")
                else:
                    st.warning("Please enter both username and password!")
    
    with col2:
        st.subheader("Sign Up")
        with st.form("signup_form"):
            new_username = st.text_input("New Username")
            new_password = st.text_input("New Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_btn = st.form_submit_button("Create Account")
            
            if signup_btn:
                if new_username and new_password and confirm_password:
                    if new_password == confirm_password:
                        success, result = create_user(new_username, new_password)
                        if success:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error(f"Error: {result}")
                    else:
                        st.error("Passwords do not match!")
                else:
                    st.warning("Please fill all fields!")

def dashboard_page():
    st.title(f"🤖 Welcome, {st.session_state.username}!")
    st.markdown("---")
    
    user_id = st.session_state.user_id
    user_config = get_user_config(user_id)
    
    if user_id not in st.session_state.automation_states:
        st.session_state.automation_states[user_id] = AutomationState()
    
    automation_state = st.session_state.automation_states[user_id]
    
    # Configuration Section
    with st.expander("⚙️ Configuration Settings", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            chat_id = st.text_input(
                "Chat ID/Thread ID",
                value=user_config['chat_id'] if user_config else '',
                help="Facebook conversation thread ID"
            )
            name_prefix = st.text_input(
                "Name Prefix", 
                value=user_config['name_prefix'] if user_config else '',
                help="Prefix to add before each message"
            )
            delay = st.number_input(
                "Delay (seconds)",
                min_value=5,
                max_value=300,
                value=user_config['delay'] if user_config else 30,
                help="Delay between messages"
            )
        
        with col2:
            cookies = st.text_area(
                "Facebook Cookies",
                value=user_config['cookies'] if user_config else '',
                height=100,
                help="Paste your Facebook cookies here"
            )
            messages = st.text_area(
                "Messages (one per line)",
                value=user_config['messages'] if user_config else 'Hello!\nHow are you?',
                height=150,
                help="Messages to send (will rotate through them)"
            )
        
        if st.button("💾 Save Configuration"):
            if update_user_config(user_id, chat_id, name_prefix, delay, cookies, messages):
                st.success("Configuration saved successfully!")
            else:
                st.error("Error saving configuration!")

    # Automation Control Section
    st.markdown("---")
    col1, col2, col3 = st.columns([1,1,2])
    
    with col1:
        if st.button("🚀 Start Automation", type="primary", use_container_width=True):
            if not chat_id:
                st.error("Please set Chat ID first!")
            else:
                start_automation(user_config, user_id)
                st.success("Automation started!")
    
    with col2:
        if st.button("🛑 Stop Automation", type="secondary", use_container_width=True):
            stop_automation(user_id)
            st.info("Automation stopped!")
    
    with col3:
        st.metric(
            "Messages Sent", 
            automation_state.message_count,
            delta=None
        )

    # Status Section
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Status")
        status_color = "🟢" if automation_state.running else "🔴"
        st.write(f"**Status:** {status_color} {'Running' if automation_state.running else 'Stopped'}")
        st.write(f"**Messages Sent:** {automation_state.message_count}")
        st.write(f"**User ID:** {user_id}")
    
    with col2:
        st.subheader("🔄 Quick Actions")
        if st.button("🔄 Refresh Status"):
            st.rerun()
        
        if st.button("📋 Clear Logs"):
            automation_state.logs = []
            st.rerun()

    # Logs Section
    st.markdown("---")
    st.subheader("📝 Activity Logs")
    
    logs_container = st.container()
    with logs_container:
        for log in automation_state.logs[-20:]:  # Show last 20 logs
            st.code(log, language="text")
    
    # Auto-refresh when running
    if automation_state.running:
        time.sleep(2)
        st.rerun()

# Main app logic
def main():
    # Initialize RAJ MISHRA on first run
    if not st.session_state.logged_in:
        initialize_raj_mishra()
    
    if st.session_state.logged_in:
        dashboard_page()
        
        # Logout button in sidebar
        with st.sidebar:
            st.write(f"Logged in as: **{st.session_state.username}**")
            if st.button("🚪 Logout"):
                # Stop automation if running
                if st.session_state.user_id in st.session_state.automation_states:
                    if st.session_state.automation_states[st.session_state.user_id].running:
                        stop_automation(st.session_state.user_id)
                
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
    else:
        login_page()

if __name__ == "__main__":
    main()
