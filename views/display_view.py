import streamlit as st
from state_manager import StateManager
import json
import os
from datetime import datetime, timedelta
import time
from utils.image_utils import get_image_as_base64

def load_panelists():
    with open("panelists.json", "r") as f:
        panelists = json.load(f)
        # Convert image paths to base64
        for panelist in panelists:
            panelist["image"] = get_image_as_base64(panelist["image"])
        return panelists

def render_panelist_card(panelist):
    team_colors = {
        "bc": "#0066cc",
        "fo": "#cc0000",
        "moderator": "#888800"
    }
    border_color = team_colors.get(panelist["team"], "#cccccc")
    st.markdown(f"""
        <div style="background:#fff; border:3px solid {border_color}; border-radius:0.5rem; padding:1rem; text-align:center; margin-bottom:1rem; width:180px; display:inline-block;">
            <img src='{panelist['image']}' style='width:90px; height:90px; object-fit:cover; border-radius:0.5rem; margin-bottom:0.5rem; border:2px solid {border_color};'>
            <div style='font-weight:bold; font-size:1.05rem; margin-bottom:0.2rem; color:#222;'>{panelist['name']}</div>
            <div style='font-size:0.95rem; color:#444;'>{panelist['position']}</div>
            <div style='font-size:0.9rem; color:#888;'>{panelist['company']}</div>
        </div>
    """, unsafe_allow_html=True)

def show_display_view(state_manager: StateManager):
    # Static styles are now in utils/styles.py
    st.markdown("""
        <h1 style='text-align:center;'>
            What do F&O and BC Have in Common? The Same Mistakes Made by Consultants!
        </h1>
    """, unsafe_allow_html=True)
    
    # Get current state
    state = state_manager.get_state()
    
    # --- Current Question ---
    if state["active_question"] is not None:
        active_q = next((q for q in state["questions"] if q["id"] == state["active_question"]), None)
        if active_q:
            st.markdown(f"""
                <div style='background:#fff; border:2px solid #0066cc; border-radius:0.5rem; padding:2rem; margin:1rem auto; max-width:900px; text-align:center; font-size:2.2rem; font-weight:bold; color:#111;'>
                    {active_q['text']}
                </div>
            """, unsafe_allow_html=True)
        else:
            st.info("No active question selected.")
    else:
        st.info("Waiting for the moderator to select a question...")

    # --- Scores ---
    col1, col2 = st.columns(2)
    blur_style = "filter: blur(8px);" if state["display_settings"]["scores_blurred"] else ""
    with col1:
        st.markdown(f"""
            <div style='background:#e6f3ff; color:#0066cc; border:2px solid #0066cc; border-radius:0.5rem; padding:1.5rem; text-align:center; font-size:2.2rem; font-weight:bold;'>
                Business Central<br><span style='{blur_style}'>{state['votes']['bc']}</span> points
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style='background:#fff0f0; color:#cc0000; border:2px solid #cc0000; border-radius:0.5rem; padding:1.5rem; text-align:center; font-size:2.2rem; font-weight:bold;'>
                Finance & Operations<br><span style='{blur_style}'>{state['votes']['fo']}</span> points
            </div>
        """, unsafe_allow_html=True)

    # --- Panelists ---
    st.markdown("<h2 style='text-align:center; margin-top:2rem;'>Panelists</h2>", unsafe_allow_html=True)
    panelists = load_panelists()
    bc_panelists = [p for p in panelists if p["team"] == "bc"]
    fo_panelists = [p for p in panelists if p["team"] == "fo"]
    moderator = [p for p in panelists if p["team"] == "moderator"]

    # Arrange: (empty) | BC1 | BC2 | MOD | FO1 | FO2 | (empty)
    panelist_row = [None] + bc_panelists + moderator + fo_panelists + [None]
    cols = st.columns(7)
    for i, p in enumerate(panelist_row):
        with cols[i]:
            if p:
                render_panelist_card(p)

    # --- Past Questions ---
    if state["past_questions"]:
        st.markdown("<h2 style='text-align:center; margin-top:2rem;'>Past Questions</h2>", unsafe_allow_html=True)
        for past_q in reversed(state["past_questions"][-3:]):  # Show last 3 past questions
            st.markdown(f"""
                <div class="past-question">
                    {past_q['text']}<br>
                    <span style='font-size:1rem; color:#888;'>
                        BC: {past_q['votes']['bc']} | FO: {past_q['votes']['fo']}
                    </span>
                </div>
            """, unsafe_allow_html=True)

def run_auto_refreshing_display_view(state_manager: StateManager, interval_seconds: int = 2):
    """
    Renders the display view and then schedules the script to rerun after a specified interval.
    This function should be called at the top level of your Streamlit script.
    """
    show_display_view(state_manager)  # Render the UI
    
    # Wait for the specified interval
    time.sleep(interval_seconds)
    
    # Trigger a rerun of the entire Streamlit script from the top
    st.rerun() 