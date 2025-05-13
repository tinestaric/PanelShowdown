from database import Database

class StateManager:
    def __init__(self, db_file: str = "panel_showdown.db"):
        self.db = Database(db_file)
    
    def add_question(self, text: str, author: str) -> int:
        """Add a new question and return its ID."""
        return self.db.add_question(text, author)
    
    def set_active_question(self, question_id: int | None) -> None:
        """Set the active question (None to clear)."""
        self.db.set_active_question(question_id)
    
    def vote(self, question_id: int, team: str, attendee_id: str) -> bool:
        """
        Record a vote for a question. Returns True if vote was recorded, False if attendee already voted.
        
        Args:
            question_id: The ID of the question being voted on
            team: The team being voted for ('bc' or 'fo')
            attendee_id: Unique identifier for the attendee (e.g., session ID or user name)
        """
        return self.db.vote(question_id, team, attendee_id)
    
    def has_voted(self, question_id: int, attendee_id: str) -> tuple[bool, str | None]:
        """
        Check if an attendee has voted for a question.
        Returns a tuple of (has_voted, team_voted_for).
        """
        return self.db.has_voted(question_id, attendee_id)
    
    def remove_question(self, question_id: int) -> None:
        """Remove a question from the queue."""
        self.db.remove_question(question_id)
    
    def reset_votes(self) -> None:
        """Reset all votes."""
        self.db.reset_votes()
    
    def reset_questions(self) -> None:
        """Reset all questions (both current and past) and their associated votes."""
        self.db.reset_questions()
    
    def get_state(self) -> dict:
        """Get the current state."""
        return self.db.get_state()
    
    def cleanup(self):
        """Clean up resources."""
        pass  # SQLite connections are automatically closed when they go out of scope 

    def add_votes(self, question_id: int, team: str, amount: int) -> None:
        """Add a specified number of votes to a question and update team score."""
        self.db.add_votes(question_id, team, amount)

    def subtract_votes(self, question_id: int, team: str, amount: int) -> None:
        """Subtract a specified number of votes from a question and update team score."""
        self.db.subtract_votes(question_id, team, amount)

    def load_initial_questions(self, json_file: str) -> None:
        """Load initial questions from a JSON file."""
        import json
        with open(json_file, 'r') as f:
            data = json.load(f)
            self.db.load_initial_questions(data["questions"])

    def toggle_scores_blur(self) -> bool:
        """Toggle the blur state of scores and return the new state."""
        return self.db.toggle_scores_blur() 