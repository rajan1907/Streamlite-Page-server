#!/usr/bin/env python3
"""
Facebook Messenger Automation Bot - FINAL RELIABILITY VERSION (FIXED)
"""

import streamlit as st
import json
import time
import threading
import os
import queue 
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException

# ============================================
# GLOBAL CONFIGURATION (Streamlit Paths)
# ============================================
LOG_QUEUE = queue.Queue()
RERUN_QUEUE = queue.Queue()  # 🆕 NEW: Thread-safe rerun requests
CHROME_PATH = "/usr/bin/google-chrome"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver" 

# ============================================
# PAGE CONFIGURATION
# ============================================
st.set_page_config(
    page_title="FB Messenger Bot", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ... (CSS STYLING - Keep your original CSS here) ...

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
def init_session_state():
    """Initialize all session state variables with default values"""
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'stop_requested' not in st.session_state:
        st.session_state.stop_requested = False
    if 'automation_thread' not in st.session_state:
        st.session_state.automation_thread = None
    if 'last_rerun' not in st.session_state:  # 🆕 NEW
        st.session_state.last_rerun = 0

# Initialize session state at startup
init_session_state()

# ============================================
# HELPER FUNCTIONS (Updated)
# ============================================

def add_log(message):
    """Thread-safe log addition."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] AUTO-1: {message}"
    LOG_QUEUE.put(log_entry)

def request_rerun():  # 🆕 NEW FUNCTION
    """Thread-safe rerun request"""
    RERUN_QUEUE.put(True)

def process_queues():  # 🆕 NEW FUNCTION
    """Update session state from queues."""
    has_updates = False
    
    # Process logs
    while not LOG_QUEUE.empty():
        try:
            log_entry = LOG_QUEUE.get_nowait()
            st.session_state.logs.append(log_entry)
            has_updates = True
        except queue.Empty:
            break
    
    # Process rerun requests (limit frequency)
    current_time = time.time()
    if not RERUN_QUEUE.empty() and (current_time - st.session_state.last_rerun) > 1:
        try:
            RERUN_QUEUE.get_nowait()
            st.session_state.last_rerun = current_time
            return True  # Signal that rerun is needed
        except queue.Empty:
            pass
    
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-100:]
        
    return has_updates

# setup_chrome_driver: Relying on external packages.txt for installation
def setup_chrome_driver():
    """Setup Chrome driver using hardcoded paths for Streamlit Cloud."""
    try:
        chrome_options = Options()
        
        # CRITICAL HEADLESS ARGUMENTS
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Check if binaries exist (relying on packages.txt to install them)
        if os.path.exists(CHROME_PATH):
            chrome_options.binary_location = CHROME_PATH
        else:
             add_log(f"❌ CRITICAL: Chrome binary not found at {CHROME_PATH}.")
             return None

        if not os.path.exists(CHROMEDRIVER_PATH):
             add_log(f"❌ CRITICAL: ChromeDriver not found at {CHROMEDRIVER_PATH}.")
             return None
        
        # Use Service directly without webdriver_manager
        service = Service(executable_path=CHROMEDRIVER_PATH)
        
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        add_log("✅ ChromeDriver setup completed and browser launched!")
        return driver
        
    except WebDriverException as e:
        add_log(f"❌ WebDriver Exception: Check `packages.txt` for dependencies. Error: {str(e)[:100]}")
        return None
    except Exception as e:
        add_log(f"❌ General ChromeDriver setup failed: {str(e)[:100]}")
        return None


def parse_cookies(cookie_string):
    """Parse cookies from various formats (Same as your original logic)"""
    cookies = []
    try:
        # Try JSON format first
        if cookie_string.strip().startswith('[') or cookie_string.strip().startswith('{'):
            cookie_data = json.loads(cookie_string)
            return cookie_data if isinstance(cookie_data, list) else [cookie_data]
        
        # Parse different delimited formats
        cookie_pairs = []
        if ';' in cookie_string:
            cookie_pairs = cookie_string.split(';')
        elif '\n' in cookie_string or '\r' in cookie_string:
            cookie_pairs = cookie_string.replace('\r\n', '\n').split('\n')
        elif ',' in cookie_string and '=' in cookie_string:
            cookie_pairs = cookie_string.split(',')
        else:
            cookie_pairs = [cookie_string]
        
        for pair in cookie_pairs:
            pair = pair.strip()
            if '=' in pair and pair:
                key, value = pair.split('=', 1)
                cookies.append({
                    'name': key.strip(), 
                    'value': value.strip(), 
                    'domain': '.facebook.com'
                })
        return cookies
    except Exception as e:
        add_log(f"❌ Cookie parsing error: {str(e)}")
        return []

# ============================================
# AUTOMATION FUNCTION (Runs in background thread)
# ============================================

def run_automation(cookies_str, messages, thread_id, delay):
    """
    Main automation function with robust messaging logic.
    """
    is_stop_requested = False
    driver = None
    
    try:
        add_log("🚀 Starting automation...")
        if st.session_state.stop_requested: return
        
        driver = setup_chrome_driver()
        if not driver:
            add_log("❌ Browser setup failed. Automation stopping.")
            return
            
        add_log("🌐 Navigating and setting cookies...")
        driver.get("https://www.facebook.com")
        time.sleep(3)
        
        cookies = parse_cookies(cookies_str)
        if not cookies:
            add_log("❌ Failed to parse cookies")
            return
        
        add_log(f"🍪 Adding {len(cookies)} cookies...")
        for cookie in cookies:
            try:
                # Use a cleaner dictionary for add_cookie
                driver.add_cookie({
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie.get('domain', '.facebook.com'),
                    'path': cookie.get('path', '/')
                })
            except Exception as e:
                add_log(f"⚠️ Cookie failed: {cookie.get('name', 'unknown')}. Error: {str(e)[:50]}")
        
        # 🆕 CHANGED: Use E2EE Messenger URL format
        thread_url = f"https://www.facebook.com/messages/e2ee/t/{thread_id}"
        add_log(f"💬 Opening E2EE conversation: {thread_id}")
        driver.get(thread_url)
        time.sleep(7) # Increased wait time for Messenger to load
        
        if "login" in driver.current_url.lower() or "checkpoint" in driver.current_url.lower():
            add_log("❌ Login/Checkpoint page detected! Cookies are invalid or expired.")
            return
        
        # Process messages
        message_list = [msg.strip() for msg in messages.split('\n') if msg.strip()]
        add_log(f"📝 Messages to send: {len(message_list)}")
        
        # 🚨 FINAL RELIABLE SELECTORS (Priority based on latest FB structure)
        INPUT_SELECTORS = [
            'div[contenteditable="true"][role="textbox"]',
            'div[aria-label="Message" i][contenteditable="true"]',
            'div[role="textbox"]',
        ]
        SEND_BUTTON_SELECTOR = 'div[role="button"][aria-label="Send"]'
        
        for idx, message in enumerate(message_list, 1):
            if st.session_state.stop_requested:
                add_log("⏹️ Stopped by user")
                is_stop_requested = True
                break
            
            try:
                add_log(f"🎯 Message {idx}/{len(message_list)}. Finding input...")
                
                # 1. Find message input using the list of selectors
                message_input = None
                for selector in INPUT_SELECTORS:
                    try:
                        message_input = driver.find_element(By.CSS_SELECTOR, selector)
                        if message_input:
                            add_log(f"✅ Found input with selector: {selector[:20]}...")
                            break
                    except NoSuchElementException:
                        continue
                
                if not message_input:
                    add_log("❌ Message input not found after all attempts. Skipping.")
                    continue
                
                # 2. Type and Click
                message_input.click()
                time.sleep(0.5)
                # Clear content using JS for robustness
                driver.execute_script("arguments[0].textContent = '';", message_input)
                message_input.send_keys(message)
                time.sleep(1)
                
                # 3. CRITICAL: Try Send Button first, then fallback to RETURN
                try:
                    send_button = driver.find_element(By.CSS_SELECTOR, SEND_BUTTON_SELECTOR)
                    send_button.click()
                    add_log("📤 Send button clicked.")
                except NoSuchElementException:
                    add_log("⚠️ Send button not found. Using RETURN key fallback.")
                    message_input.send_keys(Keys.RETURN)
                
                add_log(f"✅ Message {idx} sent!")
                time.sleep(delay)
                
            except Exception as e:
                add_log(f"❌ Error during message send loop: {str(e)[:100]}")
                time.sleep(2)
                continue
        
        if not is_stop_requested:
            add_log("🎉 Automation completed!")
        
    except Exception as e:
        add_log(f"❌ Critical error during run: {str(e)[:100]}")
    
    finally:
        if driver:
            try:
                driver.quit()
                add_log("🔒 Browser closed")
            except:
                pass
        
        add_log("---THREAD_FINISHED---")  # 🆕 CHANGED: Direct log instead of queue put

# ============================================
# MAIN UI (Updated RERUN)
# ============================================

def start_automation_thread(cookies, messages, thread_id, delay):
    """Start automation in background thread"""
    def wrapper():
        run_automation(cookies, messages, thread_id, delay)
    
    st.session_state.is_running = True 
    st.session_state.stop_requested = False
    
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    st.session_state.automation_thread = thread
    
    # 🆕 CHANGED: Use thread-safe rerun instead of direct st.rerun()
    request_rerun()

def main():
    
    rerun_needed = process_queues()  # 🆕 CHANGED: Use new queue processor
    
    if st.session_state.logs and st.session_state.logs[-1] == "---THREAD_FINISHED---":
        st.session_state.logs.pop() 
        st.session_state.is_running = False 
        rerun_needed = True  # 🆕 CHANGED: Set flag instead of direct rerun
        
    
    st.title("🤖 Facebook Messenger Automation Bot")
    
    # Status display
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.is_running:
            st.markdown('<p class="status-running">🟢 RUNNING</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-stopped">🔴 STOPPED</p>', unsafe_allow_html=True)
    
    with col2:
        if st.session_state.is_running:
            if st.button("⏹️ Stop Bot", key="stop_btn"):
                st.session_state.stop_requested = True
                add_log("🛑 Stop requested")  # 🆕 CHANGED: Use add_log instead of direct append
                rerun_needed = True  # 🆕 CHANGED: Set flag instead of direct rerun
    
    # Configuration
    st.markdown('<div class="config-section">', unsafe_allow_html=True)
    st.subheader("⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        thread_id = st.text_input(
            "💬 Thread ID", 
            placeholder="7936294139832001",
            help="Find in E2EE URL: /messages/e2ee/t/[THREAD_ID]",
            key="thread_id" 
        )
        
        delay = st.number_input(
            "⏰ Delay (seconds)", 
            min_value=1, 
            max_value=60, 
            value=3,
            key="delay" 
        )
    
    with col2:
        messages = st.text_area(
            "📝 Messages (one per line)",
            height=150,
            placeholder="Hello!\nHow are you?\nAutomated message",
            key="messages_input"
        )
    
    # Cookies (full width)
    cookies = st.text_area(
        "🍪 Facebook Cookies (All Formats Supported)", 
        height=100,
        placeholder="JSON: [{\"name\":\"c_user\",\"value\":\"123\",...}]\nSemicolon: c_user=123; xs=abc\nNewline: one per line",
        help="Supports: JSON, semicolon-delimited, newline-separated",
        key="cookies_input" 
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Start button
    if not st.session_state.is_running:
        if st.button("🚀 Start Automation", key="start_btn"):
            if not thread_id:
                st.error("❌ Enter Thread ID")
            elif not messages.strip():
                st.error("❌ Enter Messages")
            elif not cookies.strip():
                st.error("❌ Enter Cookies")
            else:
                add_log("🎬 Starting...")  # 🆕 CHANGED: Use add_log instead of direct append
                start_automation_thread(cookies, messages, thread_id, delay)
                rerun_needed = True  # 🆕 CHANGED: Set flag instead of direct rerun
    
    # Logs
    st.subheader("📊 Live Logs")
    
    # 🆕 CHANGED: Smart rerun logic
    if st.session_state.is_running:
        if rerun_needed or (time.time() - st.session_state.last_rerun) > 2:
            request_rerun()
    
    if st.session_state.logs:
        log_html = '<div class="log-container">'
        for log in reversed(st.session_state.logs[-50:]):
            log_html += f'<div class="log-entry">{log}</div>'
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)
    else:
        st.info("📝 Logs will appear here...")
    
    # Clear logs
    if st.session_state.logs:
        if st.button("🗑️ Clear Logs"):
            st.session_state.logs = []
            rerun_needed = True  # 🆕 CHANGED: Set flag instead of direct rerun
    
    # Instructions (Updated for E2EE URL)
    with st.expander("📖 Instructions"):
        st.markdown("""
        ### How to Use:
        
        1. **Get Cookies:**
           - Login to Facebook
           - F12 > Application > Cookies > facebook.com
           - Copy all cookies (especially `c_user` and `xs`)
        
        2. **Find Thread ID:**
           - Open Messenger conversation
           - Copy ID from E2EE URL: `/messages/e2ee/t/[ID]`
        
        3. **Configure:**
           - Paste cookies (any format)
           - Enter messages (one per line)
           - Set delay (3-5 sec recommended)
        
        4. **Start:**
           - Click "Start Automation"
           - Monitor logs closely.
        
        ### Note:
        If messages still fail, check the logs for:
        - **"❌ Login page detected!"**: Cookies are bad.
        - **"❌ Message input not found"**: Facebook's layout changed.
        """)
    
    # 🆕 CHANGED: Final rerun decision
    if rerun_needed:
        st.rerun()

if __name__ == "__main__":
    main()
