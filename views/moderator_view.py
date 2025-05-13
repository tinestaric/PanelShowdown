import streamlit as st
from state_manager import StateManager
from datetime import datetime
from .audience_view import render_question_card, format_timestamp
import json
import os

def show_moderator_view(state_manager: StateManager):
    st.title("🎯 Panel Showdown - Moderator View")
    
    # Get state
    state = state_manager.get_state()
    
    # Question management controls
    st.subheader("Question Management")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("Reset All Questions", type="primary"):
            if st.checkbox("I am sure I want to reset all questions"):
                state_manager.reset_questions()
                st.rerun()
    with col2:
        if st.button("Load Initial Questions", type="primary"):
            if st.checkbox("I am sure I want to load initial questions"):
                state_manager.load_initial_questions("data/initial_questions.json")
                st.rerun()
    with col3:
        if st.button("Reset All Votes", type="primary"):
            if st.checkbox("I am sure I want to reset all votes"):
                state_manager.reset_votes()
                st.rerun()
    with col4:
        blur_state = state["display_settings"]["scores_blurred"]
        if st.button(f"{'🔓 Unblur' if blur_state else '🔒 Blur'} Scores", type="primary"):
            state_manager.toggle_scores_blur()
            st.rerun()
    
    
    if state["active_question"] is not None:
        active_q = next((q for q in state["questions"] if q["id"] == state["active_question"]), None)
        if active_q:
            st.markdown("### Current Active Question")
            render_question_card(active_q, True)
            
            # Add point adjustment buttons for active question
            st.markdown("#### Adjust Points")
            col1, col2, col3, col4, col5, col6, col7, col8 = st.columns([1,1,1,1,1,1,1,1])
            with col1:
                if st.button("+1 BC", key="plus1_bc_active"):
                    state_manager.add_votes(active_q["id"], "bc", 1)
                    st.rerun()
            with col2:
                if st.button("-1 BC", key="minus1_bc_active"):
                    state_manager.subtract_votes(active_q["id"], "bc", 1)
                    st.rerun()
            with col3:
                if st.button("+10 BC", key="plus10_bc_active"):
                    state_manager.add_votes(active_q["id"], "bc", 10)
                    st.rerun()
            with col4:
                if st.button("-10 BC", key="minus10_bc_active"):
                    state_manager.subtract_votes(active_q["id"], "bc", 10)
                    st.rerun()
            with col5:
                if st.button("+1 FO", key="plus1_fo_active"):
                    state_manager.add_votes(active_q["id"], "fo", 1)
                    st.rerun()
            with col6:
                if st.button("-1 FO", key="minus1_fo_active"):
                    state_manager.subtract_votes(active_q["id"], "fo", 1)
                    st.rerun()
            with col7:
                if st.button("+10 FO", key="plus10_fo_active"):
                    state_manager.add_votes(active_q["id"], "fo", 10)
                    st.rerun()
            with col8:
                if st.button("-10 FO", key="minus10_fo_active"):
                    state_manager.subtract_votes(active_q["id"], "fo", 10)
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