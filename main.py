import streamlit as st
import os
import sys

# Add the current directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.setup_page import show_setup_page
from components.dashboard_page import show_dashboard_page
from database.db_service import init_database
from utils.constants import PAGES
import config

def init_session_state():
    """Initialize session state variables if they don't exist"""
    if "page" not in st.session_state:
        st.session_state.page = PAGES["SETUP"]
    
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

def set_page_config():
    """Set the page configuration"""
    st.set_page_config(
        page_title=config.APP_TITLE,
        page_icon="📊",
        layout="wide",
        initial_sidebar_state="expanded"
    )

def show_header():
    """Display the application header"""
    st.title(config.APP_TITLE)
    st.subheader("Build and monitor your tech-focused investment portfolio")
    
    # Sidebar header
    with st.sidebar:
        st.title("Settings")
        
        # Add a separator
        st.markdown("---")

def main():
    """Main function to run the application"""
    # Initialize database
    init_database()
    
    # Initialize session state
    init_session_state()
    
    # Set page configuration
    set_page_config()
    
    # Show header
    show_header()
    
    # Display the appropriate page based on the session state
    if st.session_state.page == PAGES["SETUP"]:
        show_setup_page()
    elif st.session_state.page == PAGES["DASHBOARD"]:
        show_dashboard_page()

if __name__ == "__main__":
    main()
