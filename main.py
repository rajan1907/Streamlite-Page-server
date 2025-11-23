#!/usr/bin/env python3
"""
Facebook Messenger Bot - PRINCE E2EE STYLE 💯✅
SIMPLE PLUG-AND-PLAY VERSION
"""

import streamlit as st
import json
import time
import os
import subprocess
import shutil
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# ============================================
# SIMPLE PLUG-AND-PLAY SETUP
# ============================================
try:
    from webdriver_manager.chrome import ChromeDriverManager
    WEBDRIVER_MANAGER_AVAILABLE = True
except ImportError:
    WEBDRIVER_MANAGER_AVAILABLE = False

# ============================================
# PAGE CONFIGURATION - PRINCE STYLE
# ============================================
st.set_page_config(
    page_title="PRINCE E2EE", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS STYLING - PRINCE STYLE
st.markdown("""
<style>
    .main-header { 
        color: white; 
        text-align: center; 
        padding: 20px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .stats-card { 
        background: #f8f9fa; 
        padding: 15px; 
        border-radius: 10px; 
        text-align: center;
        border-left: 4px solid #667eea;
        margin: 5px;
    }
    .config-section { 
        background-color: #f8f9fa; 
        padding: 20px; 
        border-radius: 10px; 
        margin: 10px 0; 
    }
    .log-container { 
        background-color: #0d1117; 
        color: #00ff00; 
        padding: 15px; 
        border-radius: 5px; 
        height: 400px; 
        overflow-y: scroll; 
        font-family: 'Courier New', monospace; 
        font-size: 12px;
    }
    .footer { 
        text-align: center; 
        margin-top: 20px; 
        padding: 10px;
        color: #666;
        font-size: 12px;
    }
    .success-log { color: #00ff00; }
    .error-log { color: #ff4444; }
    .warning-log { color: #ffaa00; }
</style>
""", unsafe_allow_html=True)

# ============================================
# SESSION STATE INITIALIZATION
# ============================================
def init_session_state():
    if 'logs' not in st.session_state:
        st.session_state.logs = []
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'messages_sent' not in st.session_state:
        st.session_state.messages_sent = 0
    if 'total_logs' not in st.session_state:
        st.session_state.total_logs = 0
    if 'config' not in st.session_state:
        st.session_state.config = {}
    if 'driver' not in st.session_state:
        st.session_state.driver = None

init_session_state()

# ============================================
# PRINCE STYLE FUNCTIONS - SIMPLE & WORKING
# ============================================

def add_log(message, log_type="info"):
    """Prince style logging with AUTO-1 prefix"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if log_type == "success":
        log_entry = f"[{timestamp}] ✅ AUTO-1: {message}"
    elif log_type == "error":
        log_entry = f"[{timestamp}] ❌ AUTO-1: {message}"
    elif log_type == "warning":
        log_entry = f"[{timestamp}] ⚠️ AUTO-1: {message}"
    else:
        log_entry = f"[{timestamp}] AUTO-1: {message}"
    
    st.session_state.logs.append(log_entry)
    st.session_state.total_logs = len(st.session_state.logs)
    
    if len(st.session_state.logs) > 100:
        st.session_state.logs = st.session_state.logs[-100:]

def setup_browser_simple():
    """SIMPLE PLUG-AND-PLAY BROWSER SETUP"""
    try:
        add_log("🚀 Starting browser setup...")
        
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # SIMPLE PLUG-AND-PLAY USING WEBDRIVER_MANAGER
        if WEBDRIVER_MANAGER_AVAILABLE:
            try:
                add_log("📥 Downloading ChromeDriver automatically...")
                service = Service(ChromeDriverManager().install())
                driver = webdriver.Chrome(service=service, options=chrome_options)
                add_log("✅ ChromeDriver setup completed automatically!", "success")
            except Exception as e:
                add_log(f"❌ Automatic setup failed: {str(e)}", "error")
                return None
        else:
            add_log("❌ webdriver_manager not available", "error")
            add_log("💡 Run: pip install webdriver-manager", "warning")
            return None
        
        # Remove webdriver property
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        add_log("✅ Browser setup completed successfully!", "success")
        return driver
        
    except Exception as e:
        add_log(f"❌ Browser setup failed: {str(e)}", "error")
        return None

def find_message_input_prince_style(driver):
    """Prince's 12 selector approach - FULLY WORKING"""
    add_log("🔍 Finding message input...")
    
    # PRINCE'S 12 SELECTORS (exact same working selectors)
    SELECTORS = [
        'div[contenteditable="true"][role="textbox"]',
        'div[aria-label="Message"][contenteditable="true"]',
        'div[contenteditable="true"][data-lexical-editor="true"]',
        'div[aria-label="Type a message..."]',
        'div[contenteditable="true"][spellcheck="true"]',
        'div[role="textbox"][contenteditable="true"]',
        '[contenteditable="true"]',
        '[role="textbox"]',
        'div[contenteditable="true"]',
        'div[data-lexical-editor="true"]',
        'div[aria-label*="message" i]',
        'div[aria-label*="type" i]'
    ]
    
    for i, selector in enumerate(SELECTORS, 1):
        try:
            elements = driver.find_elements(By.CSS_SELECTOR, selector)
            
            for element in elements:
                try:
                    if element.is_displayed() and element.is_enabled():
                        add_log(f"✅ Found input with selector #{i}", "success")
                        return element
                except:
                    continue
        except:
            continue
    
    add_log("❌ No message input found", "error")
    return None

def send_message_prince_style(driver, message):
    """Prince's exact sending method - FULLY WORKING"""
    try:
        add_log(f"📤 Sending message: {message[:50]}...")
        
        input_field = find_message_input_prince_style(driver)
        if not input_field:
            return False
        
        # Click and focus
        try:
            driver.execute_script("arguments[0].click();", input_field)
            time.sleep(2)
        except:
            try:
                input_field.click()
                time.sleep(2)
            except:
                return False
        
        # Clear input
        try:
            driver.execute_script("arguments[0].textContent = '';", input_field)
            time.sleep(1)
        except:
            pass
        
        # Type message
        try:
            input_field.send_keys(message)
            time.sleep(2)
        except:
            return False
        
        # Find send button
        send_selectors = [
            'div[role="button"][aria-label="Send"]',
            'div[aria-label="Send"]',
            'button[aria-label="Send"]',
            'div[data-testid="mf-message-send-button"]',
        ]
        
        for selector in send_selectors:
            try:
                buttons = driver.find_elements(By.CSS_SELECTOR, selector)
                for btn in buttons:
                    try:
                        if btn.is_displayed() and btn.is_enabled():
                            driver.execute_script("arguments[0].click();", btn)
                            add_log("✅ Message sent successfully!", "success")
                            time.sleep(2)
                            return True
                    except:
                        continue
            except:
                continue
        
        # Press Enter key as fallback
        try:
            input_field.send_keys(Keys.ENTER)
            add_log("✅ Message sent with Enter key!", "success")
            time.sleep(2)
            return True
        except:
            pass
        
        return False
        
    except Exception as e:
        add_log(f"❌ Send failed: {str(e)}", "error")
        return False

# ============================================
# MAIN AUTOMATION FLOW - SIMPLE & WORKING
# ============================================

def run_automation():
    """Main automation - SIMPLE VERSION"""
    if not st.session_state.is_running:
        return
    
    # Setup browser if not already setup
    if st.session_state.driver is None:
        driver = setup_browser_simple()
        if not driver:
            st.session_state.is_running = False
            return
        st.session_state.driver = driver
    else:
        driver = st.session_state.driver
    
    try:
        # Navigate to Facebook
        add_log("🌐 Opening Facebook...")
        driver.get("https://www.facebook.com")
        time.sleep(5)
        
        # Add cookies
        add_log("🍪 Adding cookies...")
        cookies = st.session_state.config['cookies_str']
        cookie_pairs = cookies.split(';')
        
        cookies_added = 0
        for pair in cookie_pairs:
            pair = pair.strip()
            if '=' in pair:
                key, value = pair.split('=', 1)
                try:
                    driver.add_cookie({
                        'name': key.strip(),
                        'value': value.strip(),
                        'domain': '.facebook.com',
                        'path': '/',
                        'secure': True
                    })
                    cookies_added += 1
                except:
                    continue
        
        add_log(f"✅ Added {cookies_added} cookies", "success")
        
        # Navigate to E2EE chat
        thread_id = st.session_state.config['thread_id']
        thread_url = f"https://www.facebook.com/messages/e2ee/t/{thread_id}"
        
        add_log(f"💬 Opening conversation {thread_id}...")
        driver.get(thread_url)
        time.sleep(10)
        
        current_url = driver.current_url
        add_log(f"🔗 Current URL: {current_url}")
        
        if "login" in current_url.lower():
            add_log("❌ Login page detected! Cookies expired.", "error")
            st.session_state.is_running = False
            return
        
        if thread_id not in current_url:
            add_log("❌ Wrong conversation!", "error")
            st.session_state.is_running = False
            return
        
        add_log("✅ Successfully loaded E2EE conversation!", "success")
        
        # Send messages
        messages = st.session_state.config['message_list']
        total_messages = len(messages)
        
        add_log(f"📨 Starting to send {total_messages} messages...")
        
        for i, message in enumerate(messages, 1):
            if not st.session_state.is_running:
                break
                
            add_log(f"📝 Message {i}/{total_messages}: {message[:30]}...")
            
            if send_message_prince_style(driver, message):
                st.session_state.messages_sent += 1
                
                # Wait between messages
                if i < total_messages:
                    time.sleep(3)
            else:
                add_log(f"❌ Failed to send message {i}", "error")
                continue
            
        add_log("🎉 All messages completed!", "success")
        
    except Exception as e:
        add_log(f"❌ Automation error: {str(e)}", "error")
    finally:
        if st.session_state.driver and not st.session_state.is_running:
            try:
                st.session_state.driver.quit()
                add_log("✅ Browser closed", "success")
            except:
                pass
            st.session_state.driver = None

def start_automation(cookies, messages, thread_id):
    """Start automation"""
    if not WEBDRIVER_MANAGER_AVAILABLE:
        st.error("❌ Please install: pip install webdriver-manager")
        return
        
    st.session_state.is_running = True
    st.session_state.messages_sent = 0
    st.session_state.config = {
        'cookies_str': cookies,
        'thread_id': thread_id,
        'message_list': [msg.strip() for msg in messages.split('\n') if msg.strip()]
    }
    add_log("🚀 Starting automation...", "success")

def stop_automation():
    """Stop automation"""
    st.session_state.is_running = False
    add_log("🛑 Automation stopped", "warning")

# ============================================
# SIMPLE UI - PRINCE STYLE
# ============================================

def main():
    # Header - Prince Style
    st.markdown("""
    <div class="main-header">
        <h1>👤 Prince E2EE</h1>
        <p>PRINCE E2EE - Facebook Automation Tool</p>
        <p><small>Simple Plug-and-Play Version</small></p>
    </div>
    """, unsafe_allow_html=True)
    
    # Installation Alert
    if not WEBDRIVER_MANAGER_AVAILABLE:
        st.error("""
        ## ❌ Missing Dependency!
        
        Please install webdriver-manager first:
        ```bash
        pip install webdriver-manager
        ```
        
        This will automatically handle ChromeDriver installation.
        """)
    
    # Simple Configuration
    st.markdown("### ⚙️ Configuration")
    
    with st.form("prince_form"):
        thread_id = st.text_input(
            "💬 Thread ID",
            value="700469533107039",
            placeholder="700469533107039",
            help="The E2EE conversation thread ID"
        )
        
        messages = st.text_area(
            "📝 Messages (one per line)",
            height=120,
            value="Hello from Prince E2EE!",
            help="Each line = One message"
        )
        
        cookies = st.text_area(
            "🍪 Facebook Cookies",
            height=100,
            placeholder="c_user=123...; xs=abc...; fr=def...; datr=xyz...",
            help="Copy cookies from browser dev tools"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            start_btn = st.form_submit_button("🚀 Start Automation", use_container_width=True)
        
        with col2:
            if st.form_submit_button("⏹️ Stop Automation", use_container_width=True, type="secondary"):
                stop_automation()
        
        if start_btn:
            if all([thread_id.strip(), messages.strip(), cookies.strip()]):
                start_automation(cookies, messages, thread_id)
            else:
                st.error("❌ Please fill all fields!")
    
    # Status
    st.markdown("### 📊 Status")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status = "🟢 Running" if st.session_state.is_running else "🔴 Stopped"
        st.markdown(f"""
        <div class="stats-card">
            <h3>Status</h3>
            <h4>{status}</h4>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stats-card">
            <h3>Messages Sent</h3>
            <h2>{st.session_state.messages_sent}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stats-card">
            <h3>Total Logs</h3>
            <h2>{st.session_state.total_logs}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Emergency stop
    if st.session_state.is_running:
        if st.button("🛑 EMERGENCY STOP", type="primary", use_container_width=True):
            stop_automation()
            st.rerun()
    
    # Live Logs
    st.markdown("### 📋 Live Logs")
    
    auto_refresh = st.checkbox("🔄 Auto-refresh logs", value=True)
    
    if st.session_state.logs:
        log_html = '<div class="log-container">'
        for log in st.session_state.logs[-20:]:
            if "✅" in log:
                log_html += f'<div class="success-log">{log}</div>'
            elif "❌" in log:
                log_html += f'<div class="error-log">{log}</div>'
            elif "⚠️" in log:
                log_html += f'<div class="warning-log">{log}</div>'
            else:
                log_html += f'<div style="margin: 2px 0; color: #00ff00;">{log}</div>'
        log_html += '</div>'
        st.markdown(log_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="log-container">
            <div style="color: #666; text-align: center; margin-top: 180px;">
                No logs yet. Start automation to see logs here.
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Clear logs
    if st.button("🗑️ Clear Logs", use_container_width=True):
        st.session_state.logs = []
        st.session_state.total_logs = 0
        st.rerun()
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>Made with ❤️ by Prince Malhotra | © 2025 All Rights Reserved</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Run automation
    if st.session_state.is_running:
        run_automation()
        if auto_refresh:
            time.sleep(2)
            st.rerun()

if __name__ == "__main__":
    main()
