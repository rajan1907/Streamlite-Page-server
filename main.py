#!/usr/bin/env python3
"""
Facebook Messenger Automation Bot - E2EE CHAT FIXED VERSION
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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, WebDriverException, TimeoutException

# ============================================
# GLOBAL CONFIGURATION (Streamlit Paths)
# ============================================
LOG_QUEUE = queue.Queue()
RERUN_QUEUE = queue.Queue()
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

# CSS STYLING
st.markdown("""
<style>
    .status-running { color: green; font-weight: bold; font-size: 18px; }
    .status-stopped { color: red; font-weight: bold; font-size: 18px; }
    .config-section { background-color: #f0f2f6; padding: 20px; border-radius: 10px; margin: 10px 0; }
    .log-container { background-color: black; color: white; padding: 15px; border-radius: 5px; max-height: 400px; overflow-y: auto; font-family: monospace; font-size: 12px; }
    .log-entry { margin: 5px 0; padding: 5px; border-left: 3px solid #4CAF50; }
</style>
""", unsafe_allow_html=True)

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
    if 'last_rerun' not in st.session_state:
        st.session_state.last_rerun = 0

init_session_state()

# ============================================
# HELPER FUNCTIONS
# ============================================

def add_log(message):
    """Thread-safe log addition."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] AUTO-1: {message}"
    LOG_QUEUE.put(log_entry)

def request_rerun():
    """Thread-safe rerun request"""
    RERUN_QUEUE.put(True)

def process_queues():
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
    
    # Process rerun requests
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
    """Setup Chrome driver for Streamlit Cloud."""
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
        
        # Check if binaries exist
        if os.path.exists(CHROME_PATH):
            chrome_options.binary_location = CHROME_PATH
        else:
            add_log(f"❌ CRITICAL: Chrome binary not found at {CHROME_PATH}.")
            return None

        if not os.path.exists(CHROMEDRIVER_PATH):
            add_log(f"❌ CRITICAL: ChromeDriver not found at {CHROMEDRIVER_PATH}.")
            return None
        
        service = Service(executable_path=CHROMEDRIVER_PATH)
        driver = webdriver.Chrome(service=service, options=chrome_options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        add_log("✅ ChromeDriver setup completed!")
        return driver
        
    except WebDriverException as e:
        add_log(f"❌ WebDriver Exception: {str(e)[:100]}")
        return None
    except Exception as e:
        add_log(f"❌ ChromeDriver setup failed: {str(e)[:100]}")
        return None

def parse_cookies(cookie_string):
    """Parse cookies from various formats"""
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

def wait_for_messenger_load(driver, timeout=30):
    """Wait for Messenger to fully load"""
    add_log("⏳ Waiting for Messenger to load...")
    start_time = time.time()
    
    while time.time() - start_time < timeout:
        if st.session_state.stop_requested:
            return False
            
        try:
            # Check if we're still on login page
            if "login" in driver.current_url.lower() or "checkpoint" in driver.current_url.lower():
                add_log("❌ Still on login/checkpoint page")
                return False
            
            # Try to find message input or conversation area
            input_selectors = [
                'div[contenteditable="true"][role="textbox"]',
                'div[aria-label="Message" i][contenteditable="true"]',
                'div[role="textbox"]',
                '[data-testid="mwthreadlist-item"]',
                '.notranslate'
            ]
            
            for selector in input_selectors:
                try:
                    element = driver.find_element(By.CSS_SELECTOR, selector)
                    if element.is_displayed():
                        add_log("✅ Messenger loaded successfully!")
                        return True
                except:
                    continue
                    
            time.sleep(2)
            
        except Exception as e:
            add_log(f"⚠️ Waiting for load: {str(e)[:50]}")
            time.sleep(2)
    
    add_log("❌ Timeout waiting for Messenger to load")
    return False

# ============================================
# AUTOMATION FUNCTION (E2EE CHAT FIXED)
# ============================================

def run_automation(cookies_str, messages, thread_id, delay):
    """
    Main automation function for E2EE chats
    """
    is_stop_requested = False
    driver = None
    
    try:
        add_log("🚀 Starting E2EE chat automation...")
        if st.session_state.stop_requested: 
            return
        
        driver = setup_chrome_driver()
        if not driver:
            add_log("❌ Browser setup failed.")
            return
            
        # STEP 1: Navigate to Facebook first
        add_log("🌐 Navigating to Facebook...")
        driver.get("https://www.facebook.com")
        time.sleep(3)
        
        # STEP 2: Add cookies
        cookies = parse_cookies(cookies_str)
        if not cookies:
            add_log("❌ Failed to parse cookies")
            return
        
        add_log(f"🍪 Adding {len(cookies)} cookies...")
        for cookie in cookies:
            try:
                driver.add_cookie({
                    'name': cookie['name'],
                    'value': cookie['value'],
                    'domain': cookie.get('domain', '.facebook.com'),
                    'path': cookie.get('path', '/')
                })
            except Exception as e:
                add_log(f"⚠️ Cookie failed: {cookie.get('name', 'unknown')}")
        
        # STEP 3: Refresh to apply cookies
        add_log("🔄 Refreshing page with cookies...")
        driver.refresh()
        time.sleep(5)
        
        # STEP 4: Check if logged in successfully
        if "login" in driver.current_url.lower():
            add_log("❌ Still on login page - cookies may be invalid")
            return
        
        add_log("✅ Successfully logged in with cookies!")
        
        # STEP 5: Navigate directly to E2EE conversation
        thread_url = f"https://www.facebook.com/messages/e2ee/t/{thread_id}"
        add_log(f"💬 Opening E2EE conversation: {thread_id}")
        driver.get(thread_url)
        
        # STEP 6: Wait for Messenger to load
        if not wait_for_messenger_load(driver):
            add_log("❌ Failed to load Messenger conversation")
            return
        
        # STEP 7: Process messages
        message_list = [msg.strip() for msg in messages.split('\n') if msg.strip()]
        add_log(f"📝 Messages to send: {len(message_list)}")
        
        # E2EE CHAT SPECIFIC SELECTORS
        INPUT_SELECTORS = [
            'div[contenteditable="true"][role="textbox"]',
            'div[aria-label="Message" i][contenteditable="true"]',
            'div[contenteditable="true"]',
            '[contenteditable="true"]',
            '.notranslate'
        ]
        
        SEND_BUTTON_SELECTORS = [
            'div[role="button"][aria-label="Send"]',
            '[aria-label="Send"]',
            '[data-testid="send-button"]'
        ]
        
        for idx, message in enumerate(message_list, 1):
            if st.session_state.stop_requested:
                add_log("⏹️ Stopped by user")
                is_stop_requested = True
                break
            
            try:
                add_log(f"🎯 Sending message {idx}/{len(message_list)}...")
                
                # Find message input with retry logic
                message_input = None
                for attempt in range(3):
                    if st.session_state.stop_requested:
                        break
                        
                    for selector in INPUT_SELECTORS:
                        try:
                            elements = driver.find_elements(By.CSS_SELECTOR, selector)
                            for element in elements:
                                if element.is_displayed() and element.is_enabled():
                                    message_input = element
                                    add_log(f"✅ Found input with: {selector}")
                                    break
                            if message_input:
                                break
                        except:
                            continue
                    
                    if message_input:
                        break
                    else:
                        add_log(f"🔄 Retry {attempt + 1} finding input...")
                        time.sleep(2)
                
                if not message_input:
                    add_log("❌ Message input not found")
                    continue
                
                # Clear and type message
                message_input.click()
                time.sleep(1)
                
                # Clear using multiple methods
                try:
                    driver.execute_script("arguments[0].textContent = '';", message_input)
                except:
                    try:
                        message_input.clear()
                    except:
                        pass
                
                message_input.send_keys(message)
                add_log(f"📝 Typed message: {message[:30]}...")
                time.sleep(1)
                
                # Send message
                send_success = False
                
                # Method 1: Try send button
                for selector in SEND_BUTTON_SELECTORS:
                    try:
                        send_button = driver.find_element(By.CSS_SELECTOR, selector)
                        if send_button.is_displayed() and send_button.is_enabled():
                            send_button.click()
                            add_log("📤 Send button clicked")
                            send_success = True
                            break
                    except:
                        continue
                
                # Method 2: Fallback to Enter key
                if not send_success:
                    try:
                        message_input.send_keys(Keys.RETURN)
                        add_log("📤 Sent using Enter key")
                        send_success = True
                    except:
                        add_log("❌ Failed to send message")
                
                if send_success:
                    add_log(f"✅ Message {idx} sent successfully!")
                else:
                    add_log(f"❌ Message {idx} failed to send")
                
                time.sleep(delay)
                
            except Exception as e:
                add_log(f"❌ Error sending message {idx}: {str(e)[:100]}")
                time.sleep(2)
                continue
        
        if not is_stop_requested:
            add_log("🎉 Automation completed successfully!")
        
    except Exception as e:
        add_log(f"❌ Critical error: {str(e)[:100]}")
    
    finally:
        if driver:
            try:
                driver.quit()
                add_log("🔒 Browser closed")
            except:
                pass
        
        add_log("---THREAD_FINISHED---")

# ============================================
# MAIN UI
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
    request_rerun()

def main():
    
    rerun_needed = process_queues()
    
    if st.session_state.logs and st.session_state.logs[-1] == "---THREAD_FINISHED---":
        st.session_state.logs.pop() 
        st.session_state.is_running = False 
        rerun_needed = True
        
    st.title("🤖 Facebook Messenger Automation Bot (E2EE Chat)")
    
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
                add_log("🛑 Stop requested")
                rerun_needed = True
    
    # Configuration
    st.markdown('<div class="config-section">', unsafe_allow_html=True)
    st.subheader("⚙️ E2EE Chat Configuration")
    
    col1, col2 = st.columns(2)
    
    with col1:
        thread_id = st.text_input(
            "💬 E2EE Thread ID", 
            placeholder="7936294139832001",
            help="Copy from E2EE URL: /messages/e2ee/t/[THREAD_ID]",
            key="thread_id" 
        )
        
        delay = st.number_input(
            "⏰ Delay between messages (seconds)", 
            min_value=2, 
            max_value=60, 
            value=5,
            help="Minimum 2 seconds recommended for E2EE chats",
            key="delay" 
        )
    
    with col2:
        messages = st.text_area(
            "📝 Messages (one per line)",
            height=150,
            placeholder="Hello!\nThis is an automated message\nFrom E2EE chat bot",
            key="messages_input"
        )
    
    # Cookies
    cookies = st.text_area(
        "🍪 Facebook Cookies (CRITICAL FOR E2EE)", 
        height=120,
        placeholder="Paste cookies in any format:\n- JSON: [{\"name\":\"c_user\",\"value\":\"123\"...}]\n- Semicolon: c_user=123; xs=abc\n- Newline separated",
        help="Make sure cookies include c_user, xs, and other authentication cookies",
        key="cookies_input" 
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Start button
    if not st.session_state.is_running:
        if st.button("🚀 Start E2EE Automation", type="primary", key="start_btn"):
            if not thread_id:
                st.error("❌ Enter E2EE Thread ID")
            elif not messages.strip():
                st.error("❌ Enter Messages")
            elif not cookies.strip():
                st.error("❌ Enter Cookies")
            else:
                add_log("🎬 Starting E2EE automation...")
                start_automation_thread(cookies, messages, thread_id, delay)
                rerun_needed = True
    
    # Logs
    st.subheader("📊 Live Logs")
    
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
        st.info("📝 Logs will appear here when automation starts...")
    
    # Clear logs
    if st.session_state.logs and not st.session_state.is_running:
        if st.button("🗑️ Clear Logs"):
            st.session_state.logs = []
            rerun_needed = True
    
    # Enhanced Instructions for E2EE
    with st.expander("📖 E2EE Chat Instructions"):
        st.markdown("""
        ### 🛡️ E2EE Chat Specific Instructions:
        
        1. **Get Fresh Cookies:**
           - Login to Facebook in Chrome/Firefox
           - Open Developer Tools (F12)
           - Go to Application/Storage > Cookies > https://www.facebook.com
           - Copy ALL cookies (especially: `c_user`, `xs`, `fr`, `datr`)
        
        2. **Find E2EE Thread ID:**
           - Open the secret conversation in Messenger
           - Copy from URL: `https://www.facebook.com/messages/e2ee/t/[THIS_IS_THREAD_ID]`
        
        3. **Important Notes for E2EE:**
           - Cookies must be very fresh (less than 1 hour old)
           - Use longer delays (5+ seconds) between messages
           - E2EE chats load slower, be patient
           - If failed, refresh cookies and try again
        
        ### 🔧 Troubleshooting:
        
        **If messages don't send:**
        - Cookies expired → Get fresh cookies
        - Page didn't load → Increase wait time
        - Element not found → Facebook updated UI
        
        **Common Error Messages:**
        - "Still on login page" → Cookies invalid
        - "Message input not found" → Page not loaded properly
        - "Timeout waiting" → Slow internet/Facebook loading
        """)
    
    if rerun_needed:
        st.rerun()

if __name__ == "__main__":
    main()
