import streamlit as st
from state_manager import StateManager
import json
import os
from datetime import datetime, timedelta
import time
from utils.image_utils import get_image_as_base64
from .audience_view import render_question_card  # Import the shared card renderer
import qrcode
import io
import base64

def generate_qr_code(url):
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Convert to base64 for HTML display
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return img_str

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
        <div style="background:#fff; border:3px solid {border_color}; border-radius:0.5rem; padding:0.8rem; text-align:center; margin-bottom:0.5rem; width:160px; display:inline-block;">
            <img src='{panelist['image']}' style='width:80px; height:80px; object-fit:cover; border-radius:0.5rem; margin-bottom:0.3rem; border:2px solid {border_color};'>
            <div style='font-weight:bold; font-size:0.95rem; margin-bottom:0.1rem; color:#222;'>{panelist['name']}</div>
            <div style='font-size:0.85rem; color:#444;'>{panelist['position']}</div>
            <div style='font-size:0.8rem; color:#888;'>{panelist['company']}</div>
        </div>
    """, unsafe_allow_html=True)

def show_display_view(state_manager: StateManager):
    # Add QR code in top-right corner
    qr_code = generate_qr_code("https://dynamicsminds25.streamlit.app/")
    st.markdown(f"""
        <div style='position:absolute; top:0.5rem; right:1rem; background:white; padding:0.3rem; border-radius:0.5rem; box-shadow:0 2px 4px rgba(0,0,0,0.1);'>
            <img src='data:image/png;base64,{qr_code}' style='width:80px; height:80px;'>
            <div style='font-size:0.7rem; color:#666; text-align:center; margin-top:0.1rem;'>Scan to join</div>
        </div>
    """, unsafe_allow_html=True)

    # Static styles are now in utils/styles.py
    st.markdown("""
        <h1 style='text-align:center; margin:0.5rem 0; font-size:1.8rem;'>
            What do F&O and BC Have in Common? <br> The Same Mistakes Made by Consultants!
        </h1>
    """, unsafe_allow_html=True)
    
    # Get current state
    state = state_manager.get_state()
    
    # --- Current Question ---
    if state["active_question"] is not None:
        active_q = next((q for q in state["questions"] if q["id"] == state["active_question"]), None)
        if active_q:
            st.markdown(f"""
                <div style='background:#fff; border:2px solid #0066cc; border-radius:0.5rem; padding:1rem; margin:0.5rem auto; max-width:900px; text-align:center; font-size:1.8rem; font-weight:bold; color:#111;'>
                    {active_q['text']}
                </div>
            """, unsafe_allow_html=True)

            # Add voting progress visualization
            total_votes = active_q['votes']['bc'] + active_q['votes']['fo']
            if total_votes > 0:
                bc_percentage = (active_q['votes']['bc'] / total_votes) * 100
                fo_percentage = (active_q['votes']['fo'] / total_votes) * 100
                
                st.markdown(f"""
                    <div style='margin:0.5rem auto; max-width:900px;'>
                        <div style='font-size:1rem; font-weight:bold; text-align:center; margin-bottom:0.3rem;'>
                            Current Voting Progress
                        </div>
                        <div style='display:flex; height:30px; border-radius:0.5rem; overflow:hidden;'>
                            <div style='background:#0066cc; width:{bc_percentage}%; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold;'>
                                {active_q['votes']['bc']} ({bc_percentage:.0f}%)
                            </div>
                            <div style='background:#cc0000; width:{fo_percentage}%; display:flex; align-items:center; justify-content:center; color:white; font-weight:bold;'>
                                {active_q['votes']['fo']} ({fo_percentage:.0f}%)
                            </div>
                        </div>
                        <div style='display:flex; justify-content:space-between; margin-top:0.2rem; font-size:0.8rem; color:#666;'>
                            <div>Business Central</div>
                            <div>Finance & Operations</div>
                        </div>
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
            <div style='background:#e6f3ff; color:#0066cc; border:2px solid #0066cc; border-radius:0.5rem; padding:0.8rem; text-align:center; font-size:1.8rem; font-weight:bold;'>
                Business Central<br><span style='{blur_style}'>{state['votes']['bc']}</span> points
            </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
            <div style='background:#fff0f0; color:#cc0000; border:2px solid #cc0000; border-radius:0.5rem; padding:0.8rem; text-align:center; font-size:1.8rem; font-weight:bold;'>
                Finance & Operations<br><span style='{blur_style}'>{state['votes']['fo']}</span> points
            </div>
        """, unsafe_allow_html=True)

    # --- Panelists ---
    st.markdown("<h2 style='text-align:center; margin:1rem 0 0.5rem 0; font-size:1.4rem;'>Panelists</h2>", unsafe_allow_html=True)
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
        st.markdown("<h2 style='text-align:center; margin:1rem 0 0.5rem 0; font-size:1.4rem;'>Past Questions</h2>", unsafe_allow_html=True)
        for past_q in reversed(state["past_questions"][-3:]):  # Show last 3 past questions
            render_question_card(past_q, is_past=True)
            st.markdown("<hr style='margin:0.5rem 0;'>")  # Thinner separator

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