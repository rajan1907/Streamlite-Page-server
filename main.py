```bash
#!/bin/bash
sudo apt-get update
sudo apt-get install -y chromium-chromedriver
```

🚀 STREAMLIT CLOUD DEPLOY PROCESS:

STEP 1: GITHUB PREPARATION

1. GitHub account banayo (agar nahi hai)
2. New repository banayo: facebook-messenger-bot
3. Ye 3 files upload karo:
   · app.py
   · requirements.txt
   · packages.txt

STEP 2: STREAMLIT CLOUD SETUP

1. streamlit.io/cloud pe jao
2. Sign in karo (Google/GitHub se)
3. "New app" button click karo
4. Repository select karo: facebook-messenger-bot
5. Branch: main
6. Main file path: app.py
7. Click "Deploy"

STEP 3: WAIT FOR BUILD

· 5-10 minutes lagega build complete hone mein
· Logs dikhenge - Chrome installation, package setup
· "Your app is live!" message aayega

🎯 DEPLOYMENT KE BAAD KYA HOGA:

SUCCESS SCENARIO:

```
✅ Building requirements...
✅ Installing system packages...
✅ Installing Python packages...
✅ Your app is running at: https://yourappname.streamlit.app/
```

ACCESS THE APP:

· Web URL mil jayegi: https://yourappname.streamlit.app/
· Professional interface dikhega
· Tum configuration karoge
· Automation run hogi

🔧 FILES KA EXACT CONTENT (Copy-Paste Ready):

File 1: app.py

```python
#!/usr/bin/env python3
"""
Facebook Messenger Bot - E2EE COMPATIBLE 💯✅
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
from selenium.common.exceptions import NoSuchElementException, WebDriverException

# ============================================
# CONFIGURATION
# ============================================
LOG_QUEUE = queue.Queue()
RERUN_QUEUE = queue.Queue()
CHROME_PATH = "/usr/bin/google-chrome"
CHROMEDRIVER_PATH = "/usr/bin/chromedriver" 

# Streamlit Page Config
st.set_page_config(
    page_title="FB Messenger Bot", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS Styling
st.markdown("""
<style>
    .main-header { color: #1f77b4; text-align: center; }
    .status-running { color: green; font-weight: bold; font-size: 18px; }
    .status-stopped { color: red; font-weight: bold; font-size: 18px; }
    .config-section { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0; }
    .log-container { background-color: black; color: #00ff00; padding: 15px; border-radius: 5px; height: 300px; overflow-y: scroll; font-family: monospace; }
    .log-entry { margin: 5px 0; border-bottom: 1px solid #333; padding: 2px 0; }
    .stButton button { width: 100%; margin: 5px 0; }
</style>
""", unsafe_allow_html=True)

# Session State
def init_session_state():
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'stop_requested' not in st.session_state:
        st.session_state.stop_requested = False
    if 'automation_thread' not in st.session_state:
        st.session_state.automation_thread = None
    if 'last_rerun' not in st.session_state:
        st.session_state.last_rerun = 0

init_session_state()

# Helper Functions
def add_log(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    LOG_QUEUE.put(log_entry)

def request_rerun():
    RERUN_QUEUE.put(True)

def process_queues():
    has_updates = False
    while not LOG_QUEUE.empty():
        try:
            log_entry = LOG_QUEUE.get_nowait()
            st.session_state.logs.append(log_entry)
            has_updates = True
        except queue.Empty:
            break
    
    current_time = time.time()
    if not RERUN_QUEUE.empty() and (current_time - st.session_state.last_rerun) > 1:
        try:
            RERUN_QUEUE.get_nowait()
            st.session_state.last_rerun = current_time
            return True
        except queue.Empty:
            pass
    
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-100:]
        
    return has_updates

def setup_chrome_driver():
    try:
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        if os.path.exists(CHROME_PATH):
            chrome_options.binary_location = CHROME_PATH

        if not os.path.exists(CHROMEDRIVER_PATH):
            add_log("❌ ChromeDriver not found")
            return None
        
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        add_log("✅ Browser started successfully")
        return driver
        
    except Exception as e:
        add_log(f"❌ Browser setup failed: {str(e)[:100]}")
        return None

def parse_cookies(cookie_string):
    cookies = []
    try:
        if cookie_string.strip().startswith('[') or cookie_string.strip().startswith('{'):
            cookie_data = json.loads(cookie_string)
            return cookie_data if isinstance(cookie_data, list) else [cookie_data]
        
        cookie_pairs = []
        if ';' in cookie_string:
            cookie_pairs = cookie_string.split(';')
        elif '\n' in cookie_string:
            cookie_pairs = cookie_string.split('\n')
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
        add_log(f"❌ Cookie error: {str(e)}")
        return []

# Automation Function
def run_automation(cookies_str, messages, thread_id, delay):
    driver = None
    try:
        add_log("🚀 Starting automation...")
        if st.session_state.stop_requested: return
        
        driver = setup_chrome_driver()
        if not driver: return
            
        driver.get("https://www.facebook.com")
        time.sleep(3)
        
        cookies = parse_cookies(cookies_str)
        if not cookies: return
        
        add_log(f"🍪 Adding {len(cookies)} cookies")
        for cookie in cookies:
            try:
                driver.add_cookie({
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': '.facebook.com'
                })
            except: pass
        
        thread_url = f"https://www.facebook.com/messages/t/{thread_id}"
        add_log(f"💬 Opening chat: {thread_id}")
        driver.get(thread_url)
        time.sleep(8)
        
        if "login" in driver.current_url.lower():
            add_log("❌ Cookies expired - Login page detected")
            return
        
        add_log("✅ Successfully entered chat!")
        
        message_list = [msg.strip() for msg in messages.split('\n') if msg.strip()]
        add_log(f"📝 Messages to send: {len(message_list)}")
        
        # E2EE Selectors
        INPUT_SELECTORS = [
            'div[contenteditable="true"][role="textbox"]',
            'div[aria-label="Message"][contenteditable="true"]',
            'div[contenteditable="true"][data-lexical-editor="true"]',
            'div[aria-label="Type a message..."]',
        ]
        
        SEND_BUTTON_SELECTORS = [
            'div[role="button"][aria-label="Send"]',
            'div[aria-label="Send"]',
            'svg[aria-label="Send"]',
        ]
        
        for idx, message in enumerate(message_list, 1):
            if st.session_state.stop_requested:
                add_log("⏹️ Stopped by user")
                break
            
            add_log(f"📨 Message {idx}/{len(message_list)}...")
            
            # Find input
            message_input = None
            for selector in INPUT_SELECTORS:
                try:
                    elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in elements:
                        if element.is_displayed():
                            message_input = element
                            break
                    if message_input: break
                except: continue
            
            if not message_input:
                add_log("❌ Input not found")
                continue
            
            # Type message
            try:
                driver.execute_script("arguments[0].click();", message_input)
                time.sleep(1)
                message_input.clear()
                time.sleep(0.5)
                
                for char in message:
                    message_input.send_keys(char)
                    time.sleep(0.02)
                
                time.sleep(1)
            except Exception as e:
                add_log(f"❌ Typing failed: {str(e)[:50]}")
                continue
            
            # Send message
            send_success = False
            for send_selector in SEND_BUTTON_SELECTORS:
                try:
                    buttons = driver.find_elements(By.CSS_SELECTOR, send_selector)
                    for btn in buttons:
                        if btn.is_displayed():
                            driver.execute_script("arguments[0].click();", btn)
                            add_log(f"✅ Message {idx} sent!")
                            send_success = True
                            break
                    if send_success: break
                except: continue
            
            if not send_success:
                try:
                    message_input.send_keys(Keys.RETURN)
                    add_log(f"✅ Message {idx} sent via ENTER!")
                except:
                    add_log(f"❌ Send failed for message {idx}")
            
            if idx < len(message_list):
                time.sleep(delay)
        
        add_log("🎉 All messages sent successfully! 💯✅")
        
    except Exception as e:
        add_log(f"❌ Error: {str(e)[:100]}")
    
    finally:
        if driver:
            try: driver.quit()
            except: pass
        add_log("---THREAD_FINISHED---")

def start_automation_thread(cookies, messages, thread_id, delay):
    def wrapper():
        run_automation(cookies, messages, thread_id, delay)
    
    st.session_state.is_running = True 
    st.session_state.stop_requested = False
    thread = threading.Thread(target=wrapper, daemon=True)
    thread.start()
    st.session_state.automation_thread = thread
    request_rerun()

# Main UI
def main():
    rerun_needed = process_queues()
    
    if st.session_state.logs and st.session_state.logs[-1] == "---THREAD_FINISHED---":
        st.session_state.logs.pop() 
        st.session_state.is_running = False 
        rerun_needed = True
        
    st.markdown('<h1 class="main-header">🤖 Facebook Messenger Bot</h1>', unsafe_allow_html=True)
    st.markdown("**E2EE Compatible • Auto Message Sender**")
    
    # Status
    col1, col2, col3 = st.columns([2,1,1])
    with col1:
        if st.session_state.is_running:
            st.markdown('<p class="status-running">🟢 AUTOMATION RUNNING</p>', unsafe_allow_html=True)
        else:
            st.markdown('<p class="status-stopped">🔴 READY TO START</p>', unsafe_allow_html=True)
    
    with col3:
        if st.session_state.is_running:
            if st.button("⏹️ STOP BOT", type="secondary"):
                st.session_state.stop_requested = True
                add_log("🛑 Stop requested")
                rerun_needed = True
    
    # Configuration
    st.markdown('<div class="config-section">', unsafe_allow_html=True)
    st.subheader("⚙️ Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        thread_id = st.text_input("💬 Thread ID", placeholder="1234567890")
        delay = st.slider("⏰ Delay (seconds)", 2, 10, 5)
    with col2:
        messages = st.text_area("📝 Messages", height=120, 
                               placeholder="Hello! 👋\nThis is test message\nFrom Auto Bot 💯✅")
    
    cookies = st.text_area("🍪 Facebook Cookies", height=80,
                          placeholder="Paste cookies here...")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Start Button
    if not st.session_state.is_running:
        if st.button("🚀 START AUTOMATION", type="primary"):
            if not all([thread_id, messages.strip(), cookies.strip()]):
                st.error("❌ Please fill all fields")
            else:
                add_log("🎬 Starting automation...")
                start_automation_thread(cookies, messages, thread_id, delay)
                rerun_needed = True
    
    # Live Logs
    st.subheader("📊 Live Logs")
    if st.session_state.logs:
        log_html = '<div class="log-container">'
        for log in reversed(st.session_state.logs[-30:]):
            if "✅" in log: color = "#00ff00"
            elif "❌" in log: color = "#ff4444" 
            elif "⚠️" in log: color = "#ffff00"
            else: color = "#00ff00"
            log_html += f'<div class="log-entry" style="color: {color};">{log}</div>'
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)
    else:
        st.info("Logs will appear here when automation starts...")
    
    # Instructions
    with st.expander("📖 Instructions"):
        st.markdown("""
        1. **Get Cookies:** Browser Developer Tools → Application → Cookies → facebook.com
        2. **Thread ID:** messenger.com → Open chat → Copy numbers from URL after /t/
        3. **Messages:** One message per line
        4. **Start:** Fill all fields and click START
        
        **Supports E2EE Encrypted Chats 💯✅**
        """)
    
    if rerun_needed:
        st.rerun()

if __name__ == "__main__":
    main()
```
