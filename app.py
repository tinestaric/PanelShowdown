import streamlit as st
from state_manager import StateManager
from utils.styles import inject_custom_css
from views.audience_view import run_auto_refreshing_audience_view
from views.moderator_view import show_moderator_view
from views.display_view import run_auto_refreshing_display_view
import os

# Page config - must be first Streamlit command
st.set_page_config(
    page_title="Panel Showdown",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"  # Default to expanded, we'll hide it in display view via CSS
)

# Initialize state manager
state_manager = StateManager()

# Get the current view from URL parameters
view = st.query_params.get("view", "audience")

# Inject custom CSS
inject_custom_css()

# Add view-specific CSS
if view == "display":
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {display: none;}
            .stDeployButton {display: none;}
            footer {visibility: hidden;}
        </style>
    """, unsafe_allow_html=True)

# Access control
if view not in ["audience", "moderator", "display"]:
    st.error("Invalid view specified")
    st.stop()

# Show appropriate view based on URL
if view == "audience":
    run_auto_refreshing_audience_view(state_manager)
elif view == "moderator":
    # Check for moderator access
    if "moderator" not in st.query_params.get("access", []):
        st.error("Access denied. This view is for moderators only.")
        st.stop()
    show_moderator_view(state_manager)
elif view == "display":
    # Check for display access
    if "display" not in st.query_params.get("access", []):
        st.error("Access denied. This view is for display purposes only.")
        st.stop()
    run_auto_refreshing_display_view(state_manager) 