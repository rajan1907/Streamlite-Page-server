#!/usr/bin/env python3 """ Facebook Messenger Bot- PRINCE E2EE STYLE 💯✅ FULLY WORKING VERSION- EXACT SAME AS PRINCE'S WORKING CODE """

import streamlit as st import json import time import os import subprocess from datetime import datetime from selenium import webdriver from selenium.webdriver.common.by import By from selenium.webdriver.chrome.options import Options from selenium.webdriver.chrome.service import Service from selenium.webdriver.common.keys import Keys from selenium.webdriver.support.ui import WebDriverWait from selenium.webdriver.support import expected_conditions as EC

============================================

GLOBAL CONFIGURATION - PRINCE STYLE

============================================

CHROME_PATH = "/usr/bin/chromium" CHROMEDRIVER_PATH= "/usr/bin/chromedriver"

============================================

PAGE CONFIGURATION - PRINCE STYLE

============================================

st.set_page_config( page_title="PRINCE E2EE",  layout="wide", initial_sidebar_state="expanded" )

CSS STYLING - PRINCE STYLE

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

============================================

SESSION STATE INITIALIZATION

============================================

def init_session_state(): if 'logs' not in st.session_state: st.session_state.logs = [] if 'is_running' not in st.session_state: st.session_state.is_running = False if 'messages_sent' not in st.session_state: st.session_state.messages_sent = 0 if 'total_logs' not in st.session_state: st.session_state.total_logs = 0 if 'config' not in st.session_state: st.session_state.config = {} if 'driver' not in st.session_state: st.session_state.driver = None

init_session_state()

============================================

PRINCE STYLE FUNCTIONS - FULLY WORKING

============================================

def add_log(message, log_type="info"): """Prince style logging with AUTO-1 prefix""" timestamp = datetime.now().strftime("%H:%M:%S")

def setup_browser_prince_style(): """Prince's exact browser setup - FULLY WORKING""" try: add_log("Setting up Chrome browser...")

def find_message_input_prince_style(driver): """Prince's 12 selector approach - FULLY WORKING""" add_log("Finding message input...") add_log(f"Page Title: {driver.title}") add_log(f"Page URL: {driver.current_url}")

def send_message_prince_style(driver, message): """Prince's exact sending method - FULLY WORKING""" try: add_log(f"Attempting to send message: {message[:50]}...")

def wait_for_element(driver, selector, timeout=30): """Wait for element to be present""" try: element = WebDriverWait(driver, timeout).until( EC.presence_of_element_located((By.CSS_SELECTOR, selector)) ) return element except: return None

============================================

MAIN AUTOMATION FLOW - PRINCE STYLE FULLY WORKING

============================================

def run_automation(): """Main automation like Prince - FULLY WORKING""" if not st.session_state.is_running: return

def start_automation(cookies, messages, thread_id): """Start automation""" st.session_state.is_running = True st.session_state.messages_sent = 0 st.session_state.config = { 'cookies_str': cookies, 'thread_id': thread_id, 'message_list': [msg.strip() for msg in messages.split('\n') if msg.strip()] } add_log("🚀 Starting automation...", "success") add_log(f"Target: E2EE Thread {thread_id}", "success") add_log(f"Messages to send: {len(st.session_state.config['message_list'])}", "success")

def stop_automation(): """Stop automation""" st.session_state.is_running = False add_log("🛑 Automation stopped by user", "warning")

============================================

PRINCE STYLE UI - FULLY WORKING

============================================

def main(): # Header - Prince Style st.markdown(""" <div class="main-header"> <h1>👤 Prince E2EE</h1> <p>PRINCE E2EE - Facebook Automation Tool</p> <p><small>Created by Prince Malhotra</small></p> </div> """, unsafe_allow_html=True)

if name == "main": main()

isme se app.py dena
