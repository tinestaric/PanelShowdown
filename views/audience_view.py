import streamlit as st
from state_manager import StateManager
from datetime import datetime, timedelta
import time
import uuid

def get_attendee_id():
    """Get or create a unique attendee ID for this session."""
    if "attendee_id" not in st.session_state:
        st.session_state.attendee_id = str(uuid.uuid4())
    return st.session_state.attendee_id

def render_question_card(question, is_active=False, is_past=False, has_voted=False, voted_team=None):
    card_class = "question-card active-question" if is_active else "question-card"
    if is_past:
        card_class += " past-question"
    
    if question.get("winner") == "bc":
        team_color = "#0066cc"
    elif question.get("winner") == "fo":
        team_color = "#cc0000"
    else:
        team_color = "#888888"  # Gray color for no winner or other cases
    
    winner = question.get('winner', '').upper() if question.get('winner') else "none"
    
    st.markdown(f"""
        <div class="{card_class}">
            <div class="question-text"><strong>Q:</strong> {question['text']}</div>
            <div class="question-meta">
                By: {question['author']} at {format_timestamp(question['timestamp'])}<br>
                Votes: BC ({question['votes']['bc']}) | FO ({question['votes']['fo']})
            </div>
            <div class="winner-info" style="color:{team_color}">
                <strong>Point awarded to {winner}</strong>
            </div>
        </div>
    """, unsafe_allow_html=True)


    if has_voted:
        team_color = "#0066cc" if voted_team == "bc" else "#cc0000"
        vote_status = f"""
            <div style='width:100%; text-align:center;'>
                <div style='margin-top:0.5rem; padding:0.3rem; background:{team_color}; color:white; border-radius:0.3rem; display:inline-block;'>
                    Voted for {voted_team.upper()}
                </div>
            </div>
        """
        st.markdown(vote_status, unsafe_allow_html=True)

def format_timestamp(timestamp):
    dt = datetime.fromisoformat(timestamp)
    return dt.strftime("%H:%M:%S")

def show_audience_view(state_manager: StateManager):
    st.title("🎯 Panel Showdown")
    
    # Get state
    state = state_manager.get_state()
    attendee_id = get_attendee_id()
    
    # Handle success message
    if "show_submit_success" in st.session_state and st.session_state.show_submit_success:
        st.success("Question submitted successfully!")
        st.session_state.show_submit_success = False  # Clear the flag after showing
    
    # Question submission
    with st.form("question_form", clear_on_submit=True):
        st.subheader("Submit a Question")
        question = st.text_area("Your question", height=100)
        author = st.text_input("Your name")
        submitted = st.form_submit_button("Submit Question")
        
        if submitted and question and author:
            state_manager.add_question(question, author)
            st.session_state.show_submit_success = True  # Set flag to show success message
            st.rerun()  # Rerun to get fresh state with new question
    
    # Active question display
    st.subheader("Current Question")
    
    if state["active_question"] is not None:
        active_q = next((q for q in state["questions"] if q["id"] == state["active_question"]), None)
        if active_q:
            has_voted, voted_team = state_manager.has_voted(active_q["id"], attendee_id)
            render_question_card(active_q, True, has_voted=has_voted, voted_team=voted_team)
            
            # Only show voting buttons if question is not locked and user hasn't voted
            if not active_q.get("winner") and not has_voted:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Vote Business Central", key="vote_bc_active"):
                        if state_manager.vote(active_q["id"], "bc", attendee_id):
                            st.success("Vote recorded!")
                        else:
                            st.error("You have already voted for this question!")
                        st.rerun()
                with col2:
                    if st.button("Vote Finance & Operations", key="vote_fo_active"):
                        if state_manager.vote(active_q["id"], "fo", attendee_id):
                            st.success("Vote recorded!")
                        else:
                            st.error("You have already voted for this question!")
                        st.rerun()
            elif has_voted:
                st.info(f"You have already voted for {voted_team.upper()}")
            elif active_q.get("winner"):
                st.info(f"Voting is closed. Point awarded to {active_q['winner'].upper()}")
    else:
        st.info("Waiting for the moderator to select a question...")

    # Past questions display
    if state["past_questions"]:
        st.subheader("Past Questions")
        for past_q in reversed(state["past_questions"]):  # Show most recent first
            has_voted, voted_team = state_manager.has_voted(past_q["id"], attendee_id)
            render_question_card(past_q, is_past=True, has_voted=has_voted, voted_team=voted_team)
            
            # Only show voting buttons if question is not locked and user hasn't voted
            if not past_q.get("winner") and not has_voted:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Vote BC", key=f"vote_bc_past_{past_q['id']}"):
                        if state_manager.vote(past_q["id"], "bc", attendee_id):
                            st.success("Vote recorded!")
                        else:
                            st.error("You have already voted for this question!")
                        st.rerun()
                with col2:
                    if st.button("Vote FO", key=f"vote_fo_past_{past_q['id']}"):
                        if state_manager.vote(past_q["id"], "fo", attendee_id):
                            st.success("Vote recorded!")
                        else:
                            st.error("You have already voted for this question!")
                        st.rerun()
            elif has_voted:
                st.info(f"You have already voted for {voted_team.upper()}")
            elif past_q.get("winner"):
                st.info(f"Voting is closed. Point awarded to {past_q['winner'].upper()}")
            st.markdown("---")  # Add a separator between past questions

def run_auto_refreshing_audience_view(state_manager: StateManager, interval_seconds: int = 2):
    """
    Renders the audience view and then schedules the script to rerun after a specified interval.
    """
    show_audience_view(state_manager)  # Render the UI
    
    # Wait for the specified interval
    time.sleep(interval_seconds)
    
    # Trigger a rerun of the entire Streamlit script from the top
    st.rerun() 