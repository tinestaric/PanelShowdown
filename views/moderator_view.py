import streamlit as st
from state_manager import StateManager
from datetime import datetime
from .audience_view import render_question_card, format_timestamp
import json
import os

def confirm_action(action_key: str, action_name: str, on_confirm):
    """Helper function to handle confirmation flow for destructive actions.
    
    Args:
        action_key: Unique key for this action in session state
        action_name: Display name of the action for the confirmation message
        on_confirm: Callback function to execute when confirmed
    """
    # Initialize session state for this action if not exists
    if f'confirm_{action_key}' not in st.session_state:
        st.session_state[f'confirm_{action_key}'] = False
        
    if st.button(action_name, type="primary"):
        st.session_state[f'confirm_{action_key}'] = True
        
    if st.session_state[f'confirm_{action_key}']:
        if st.checkbox(f"I am sure I want to {action_name.lower()}", key=f"confirm_checkbox_{action_key}"):
            on_confirm()
            st.session_state[f'confirm_{action_key}'] = False  # Reset the confirmation state
            st.rerun()

def show_moderator_view(state_manager: StateManager):
    st.title("🎯 Panel Showdown - Moderator View")
    
    # Get state
    state = state_manager.get_state()
    
    # Question management controls
    st.subheader("Question Management")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        confirm_action(
            "reset_questions",
            "Reset All Questions",
            lambda: state_manager.reset_questions()
        )
    with col2:
        confirm_action(
            "load_initial",
            "Load Initial Questions",
            lambda: state_manager.load_initial_questions("data/initial_questions.json")
        )
    with col3:
        confirm_action(
            "reset_votes",
            "Reset All Votes",
            lambda: state_manager.reset_votes()
        )
    with col4:
        blur_state = state["display_settings"]["scores_blurred"]
        if st.button(f"{'🔓 Unblur' if blur_state else '🔒 Blur'} Scores", type="primary"):
            state_manager.toggle_scores_blur()
            st.rerun()
    
    # Manual score adjustment (for fun!)
    st.subheader("🎮 Manual Score Adjustment")
    st.markdown("> *For moderator's entertainment only!* 😈")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Business Central")
        bc_col1, bc_col2 = st.columns(2)
        with bc_col1:
            if st.button("➕ Add 10", key="bc_add_10", type="primary"):
                state_manager.add_votes(state["active_question"] or 0, "bc", 10)
                st.rerun()
        with bc_col2:
            if st.button("➖ Subtract 10", key="bc_sub_10", type="secondary"):
                state_manager.subtract_votes(state["active_question"] or 0, "bc", 10)
                st.rerun()
    with col2:
        st.markdown("#### Finance & Operations")
        fo_col1, fo_col2 = st.columns(2)
        with fo_col1:
            if st.button("➕ Add 10", key="fo_add_10", type="primary"):
                state_manager.add_votes(state["active_question"] or 0, "fo", 10)
                st.rerun()
        with fo_col2:
            if st.button("➖ Subtract 10", key="fo_sub_10", type="secondary"):
                state_manager.subtract_votes(state["active_question"] or 0, "fo", 10)
                st.rerun()
    
    if state["active_question"] is not None:
        active_q = next((q for q in state["questions"] if q["id"] == state["active_question"]), None)
        if active_q:
            st.markdown("### Current Active Question")
            render_question_card(active_q, True)
            
            # Always show winner selection buttons, highlight the current winner
            st.markdown("#### Select Winner")
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "Award Point to BC" + (" (Current)" if active_q.get("winner") == "bc" else ""),
                    type="primary" if active_q.get("winner") == "bc" else "secondary",
                    key="winner_bc"
                ):
                    state_manager.set_question_winner(active_q["id"], "bc")
                    st.rerun()
            with col2:
                if st.button(
                    "Award Point to FO" + (" (Current)" if active_q.get("winner") == "fo" else ""),
                    type="primary" if active_q.get("winner") == "fo" else "secondary",
                    key="winner_fo"
                ):
                    state_manager.set_question_winner(active_q["id"], "fo")
                    st.rerun()
            
            if st.button("Clear Active Question"):
                state_manager.set_active_question(None)
                st.rerun()
    
    # Question management
    st.subheader("Question Queue")
    for question in state["questions"]:
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            render_question_card(question, question["id"] == state["active_question"])
        with col2:
            if st.button("Set Active", key=f"active_{question['id']}"):
                state_manager.set_active_question(question["id"])
                st.rerun()
        with col3:
            if st.button("Remove", key=f"remove_{question['id']}"):
                state_manager.remove_question(question["id"])
                st.rerun()
    
    # Past questions management
    if state["past_questions"]:
        st.subheader("Past Questions")
        for past_q in reversed(state["past_questions"]):  # Show most recent first
            render_question_card(past_q, is_past=True)
            if st.button("Make Active", key=f"reactivate_{past_q['id']}"):
                state_manager.set_active_question(past_q["id"])
                st.rerun()
            st.markdown("---") 