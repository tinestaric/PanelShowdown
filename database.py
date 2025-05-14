import sqlite3
from datetime import datetime
from typing import Dict, List, Optional

class Database:
    def __init__(self, db_file: str = "panel_showdown.db"):
        self.db_file = db_file
        self._initialize_db()
    
    def _get_connection(self):
        """Get a database connection with proper row factory."""
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        return conn
    
    def _initialize_db(self):
        """Initialize the database with required tables if they don't exist."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Create questions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS questions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    text TEXT NOT NULL,
                    author TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 0,
                    is_past BOOLEAN DEFAULT 0,
                    winner TEXT CHECK(winner IN ('bc', 'fo', NULL))
                )
            """)
            
            # Create votes table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS votes (
                    question_id INTEGER,
                    team TEXT CHECK(team IN ('bc', 'fo')),
                    count INTEGER DEFAULT 0,
                    PRIMARY KEY (question_id, team),
                    FOREIGN KEY (question_id) REFERENCES questions(id)
                )
            """)
            
            # Create individual_votes table to track per-attendee votes
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS individual_votes (
                    question_id INTEGER,
                    attendee_id TEXT NOT NULL,
                    team TEXT CHECK(team IN ('bc', 'fo')),
                    timestamp TEXT NOT NULL,
                    PRIMARY KEY (question_id, attendee_id),
                    FOREIGN KEY (question_id) REFERENCES questions(id)
                )
            """)
            
            # Create team_scores table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS team_scores (
                    team TEXT PRIMARY KEY CHECK(team IN ('bc', 'fo')),
                    score INTEGER DEFAULT 0
                )
            """)
            
            # Create display_settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS display_settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            """)
            
            # Initialize team scores if they don't exist
            cursor.execute("""
                INSERT OR IGNORE INTO team_scores (team, score)
                VALUES ('bc', 0), ('fo', 0)
            """)
            
            # Initialize display settings if they don't exist
            cursor.execute("""
                INSERT OR IGNORE INTO display_settings (key, value)
                VALUES ('scores_blurred', 'false')
            """)
            
            conn.commit()
    
    def add_question(self, text: str, author: str) -> int:
        """Add a new question and return its ID."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            timestamp = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO questions (text, author, timestamp, is_past, is_active)
                VALUES (?, ?, ?, 0, 0)
            """, (text, author, timestamp))
            question_id = cursor.lastrowid
            
            # Initialize votes for the new question
            cursor.execute("""
                INSERT INTO votes (question_id, team, count)
                VALUES (?, 'bc', 0), (?, 'fo', 0)
            """, (question_id, question_id))
            
            conn.commit()
            return question_id
    
    def set_active_question(self, question_id: Optional[int]) -> None:
        """Set the active question (None to clear). Move previous active to past questions."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # First, move current active question to past if it exists
            cursor.execute("""
                UPDATE questions 
                SET is_active = 0, is_past = 1
                WHERE is_active = 1
            """)
            
            # Then set new active question if provided
            if question_id is not None:
                cursor.execute("""
                    UPDATE questions 
                    SET is_active = 1, is_past = 0
                    WHERE id = ?
                """, (question_id,))
            
            conn.commit()
    
    def vote(self, question_id: int, team: str, attendee_id: str) -> bool:
        """
        Record a vote for a question. Returns True if vote was recorded, False if attendee already voted.
        
        Args:
            question_id: The ID of the question being voted on
            team: The team being voted for ('bc' or 'fo')
            attendee_id: Unique identifier for the attendee (e.g., session ID or user name)
        """
        if team not in ["bc", "fo"]:
            raise ValueError("Team must be 'bc' or 'fo'")
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Check if question is locked (has a winner)
            cursor.execute("""
                SELECT winner FROM questions WHERE id = ?
            """, (question_id,))
            result = cursor.fetchone()
            if result and result["winner"] is not None:
                return False  # Question is locked
            
            # Check if attendee already voted for this question
            cursor.execute("""
                SELECT 1 FROM individual_votes 
                WHERE question_id = ? AND attendee_id = ?
            """, (question_id, attendee_id))
            
            if cursor.fetchone():
                return False  # Attendee already voted
            
            # Record the individual vote
            timestamp = datetime.now().isoformat()
            cursor.execute("""
                INSERT INTO individual_votes (question_id, attendee_id, team, timestamp)
                VALUES (?, ?, ?, ?)
            """, (question_id, attendee_id, team, timestamp))
            
            # Update question vote count
            cursor.execute("""
                UPDATE votes 
                SET count = count + 1
                WHERE question_id = ? AND team = ?
            """, (question_id, team))
            
            conn.commit()
            return True
    
    def has_voted(self, question_id: int, attendee_id: str) -> tuple[bool, str | None]:
        """
        Check if an attendee has voted for a question.
        Returns a tuple of (has_voted, team_voted_for).
        """
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT team FROM individual_votes 
                WHERE question_id = ? AND attendee_id = ?
            """, (question_id, attendee_id))
            result = cursor.fetchone()
            if result:
                return True, result["team"]
            return False, None
    
    def remove_question(self, question_id: int) -> None:
        """Remove a question from the queue."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Remove votes first (due to foreign key constraint)
            cursor.execute("DELETE FROM votes WHERE question_id = ?", (question_id,))
            
            # Then remove the question
            cursor.execute("DELETE FROM questions WHERE id = ?", (question_id,))
            
            conn.commit()
    
    def reset_votes(self) -> None:
        """Reset all votes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Reset all vote counts
            cursor.execute("UPDATE votes SET count = 0")
            
            # Reset team scores
            cursor.execute("UPDATE team_scores SET score = 0")
            
            conn.commit()
    
    def reset_questions(self) -> None:
        """Reset all questions (both current and past) and their associated votes."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Delete all votes first (due to foreign key constraint)
            cursor.execute("DELETE FROM votes")
            cursor.execute("DELETE FROM individual_votes")
            
            # Delete all questions
            cursor.execute("DELETE FROM questions")
            
            # Reset team scores
            cursor.execute("UPDATE team_scores SET score = 0")
            
            conn.commit()
    
    def get_state(self) -> Dict:
        """Get the current state."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get display settings
            cursor.execute("SELECT value FROM display_settings WHERE key = 'scores_blurred'")
            scores_blurred = cursor.fetchone()["value"] == "true"
            
            # Get active question
            cursor.execute("""
                SELECT id, winner FROM questions WHERE is_active = 1
            """)
            active_question = cursor.fetchone()
            active_question_id = active_question["id"] if active_question else None
            active_question_winner = active_question["winner"] if active_question else None
            
            # Get all questions with their votes
            cursor.execute("""
                SELECT q.*, 
                       v_bc.count as bc_votes,
                       v_fo.count as fo_votes
                FROM questions q
                LEFT JOIN votes v_bc ON q.id = v_bc.question_id AND v_bc.team = 'bc'
                LEFT JOIN votes v_fo ON q.id = v_fo.question_id AND v_fo.team = 'fo'
                WHERE q.is_past = 0
                ORDER BY q.id
            """)
            questions = []
            for row in cursor.fetchall():
                questions.append({
                    "id": row["id"],
                    "text": row["text"],
                    "author": row["author"],
                    "votes": {
                        "bc": row["bc_votes"],
                        "fo": row["fo_votes"]
                    },
                    "timestamp": row["timestamp"],
                    "winner": row["winner"]
                })
            
            # Get past questions
            cursor.execute("""
                SELECT q.*, 
                       v_bc.count as bc_votes,
                       v_fo.count as fo_votes
                FROM questions q
                LEFT JOIN votes v_bc ON q.id = v_bc.question_id AND v_bc.team = 'bc'
                LEFT JOIN votes v_fo ON q.id = v_fo.question_id AND v_fo.team = 'fo'
                WHERE q.is_past = 1
                ORDER BY q.id DESC
            """)
            past_questions = []
            for row in cursor.fetchall():
                past_questions.append({
                    "id": row["id"],
                    "text": row["text"],
                    "author": row["author"],
                    "votes": {
                        "bc": row["bc_votes"],
                        "fo": row["fo_votes"]
                    },
                    "timestamp": row["timestamp"],
                    "winner": row["winner"]
                })
            
            # Get team scores
            cursor.execute("SELECT * FROM team_scores")
            votes = {"bc": 0, "fo": 0}
            for row in cursor.fetchall():
                votes[row["team"]] = row["score"]
            
            # Add display settings to state
            state = {
                "active_question": active_question_id,
                "questions": questions,
                "past_questions": past_questions,
                "votes": votes,
                "display_settings": {
                    "scores_blurred": scores_blurred
                },
                "last_updated": datetime.now().isoformat()
            }
            
            return state
    
    def add_votes(self, question_id: int, team: str, amount: int) -> None:
        """Add a specified number of votes to a question and update team score."""
        if team not in ["bc", "fo"]:
            raise ValueError("Team must be 'bc' or 'fo'")
        if amount < 1:
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Update question vote count
            cursor.execute("""
                UPDATE votes 
                SET count = count + ?
                WHERE question_id = ? AND team = ?
            """, (amount, question_id, team))
            # Prevent negative votes
            cursor.execute("""
                UPDATE votes 
                SET count = 0
                WHERE question_id = ? AND team = ? AND count < 0
            """, (question_id, team))
            # Update team score
            cursor.execute("""
                UPDATE team_scores 
                SET score = score + ?
                WHERE team = ?
            """, (amount, team))
            # Prevent negative team score
            cursor.execute("""
                UPDATE team_scores 
                SET score = 0
                WHERE team = ? AND score < 0
            """, (team,))
            conn.commit()

    def subtract_votes(self, question_id: int, team: str, amount: int) -> None:
        """Subtract a specified number of votes from a question and update team score. Votes cannot go below zero."""
        if team not in ["bc", "fo"]:
            raise ValueError("Team must be 'bc' or 'fo'")
        if amount < 1:
            return
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # Subtract from question vote count
            cursor.execute("""
                UPDATE votes 
                SET count = count - ?
                WHERE question_id = ? AND team = ?
            """, (amount, question_id, team))
            # Prevent negative votes
            cursor.execute("""
                UPDATE votes 
                SET count = 0
                WHERE question_id = ? AND team = ? AND count < 0
            """, (question_id, team))
            # Subtract from team score
            cursor.execute("""
                UPDATE team_scores 
                SET score = score - ?
                WHERE team = ?
            """, (amount, team))
            # Prevent negative team score
            cursor.execute("""
                UPDATE team_scores 
                SET score = 0
                WHERE team = ? AND score < 0
            """, (team,))
            conn.commit()

    def load_initial_questions(self, questions_data: list) -> None:
        """Load initial questions from a list of question data."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            # First reset all questions
            self.reset_questions()
            
            # Then insert new questions
            timestamp = datetime.now().isoformat()
            for q in questions_data:
                cursor.execute("""
                    INSERT INTO questions (text, author, timestamp, is_active, is_past)
                    VALUES (?, ?, ?, 0, 0)
                """, (q["text"], q["author"], timestamp))
                
                # Initialize votes for the question
                question_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO votes (question_id, team, count)
                    VALUES (?, 'bc', 0), (?, 'fo', 0)
                """, (question_id, question_id))
            
            conn.commit()

    def toggle_scores_blur(self) -> bool:
        """Toggle the blur state of scores and return the new state."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Get current state
            cursor.execute("SELECT value FROM display_settings WHERE key = 'scores_blurred'")
            current_state = cursor.fetchone()["value"] == "true"
            
            # Toggle state
            new_state = not current_state
            cursor.execute("""
                UPDATE display_settings 
                SET value = ? 
                WHERE key = 'scores_blurred'
            """, ("true" if new_state else "false",))
            
            conn.commit()
            return new_state

    def set_question_winner(self, question_id: int, team: str) -> None:
        """Set the winner for a question and update team scores, handling re-awards."""
        if team not in ["bc", "fo"]:
            raise ValueError("Team must be 'bc' or 'fo'")

        with self._get_connection() as conn:
            cursor = conn.cursor()

            # Get the current winner
            cursor.execute("SELECT winner FROM questions WHERE id = ?", (question_id,))
            result = cursor.fetchone()
            prev_winner = result["winner"] if result else None

            if prev_winner == team:
                # No change, do nothing
                return

            # Update the winner
            cursor.execute("""
                UPDATE questions 
                SET winner = ?
                WHERE id = ?
            """, (team, question_id))

            # Subtract a point from the previous winner, if any
            if prev_winner in ["bc", "fo"]:
                cursor.execute("""
                    UPDATE team_scores 
                    SET score = score - 1
                    WHERE team = ? AND score > 0
                """, (prev_winner,))

            # Add a point to the new winner
            cursor.execute("""
                UPDATE team_scores 
                SET score = score + 1
                WHERE team = ?
            """, (team,))

            conn.commit() 