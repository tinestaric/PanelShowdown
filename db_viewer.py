import sqlite3
from tabulate import tabulate
import sys

def get_db_connection():
    """Get a database connection with proper row factory."""
    conn = sqlite3.connect("panel_showdown.db")
    conn.row_factory = sqlite3.Row
    return conn

def view_questions():
    """View all questions with their status."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Get all questions with their votes
        cursor.execute("""
            SELECT 
                q.id,
                q.text,
                q.author,
                q.timestamp,
                q.is_active,
                q.is_past,
                v_bc.count as bc_votes,
                v_fo.count as fo_votes
            FROM questions q
            LEFT JOIN votes v_bc ON q.id = v_bc.question_id AND v_bc.team = 'bc'
            LEFT JOIN votes v_fo ON q.id = v_fo.question_id AND v_fo.team = 'fo'
            ORDER BY q.id
        """)
        
        rows = cursor.fetchall()
        if not rows:
            print("No questions in database.")
            return
        
        # Format the data for display
        headers = ["ID", "Text", "Author", "Timestamp", "Active", "Past", "BC Votes", "FO Votes"]
        data = []
        for row in rows:
            data.append([
                row["id"],
                row["text"][:50] + "..." if len(row["text"]) > 50 else row["text"],
                row["author"],
                row["timestamp"],
                "✓" if row["is_active"] else "",
                "✓" if row["is_past"] else "",
                row["bc_votes"],
                row["fo_votes"]
            ])
        
        print("\nQuestions in Database:")
        print(tabulate(data, headers=headers, tablefmt="grid"))
        
        # Print summary
        active = sum(1 for row in rows if row["is_active"])
        past = sum(1 for row in rows if row["is_past"])
        current = sum(1 for row in rows if not row["is_past"])
        print(f"\nSummary: {len(rows)} total questions")
        print(f"  - {active} active")
        print(f"  - {current} current (non-past)")
        print(f"  - {past} past")

def view_team_scores():
    """View team scores."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM team_scores ORDER BY team")
        rows = cursor.fetchall()
        
        if not rows:
            print("No team scores in database.")
            return
        
        headers = ["Team", "Score"]
        data = [[row["team"].upper(), row["score"]] for row in rows]
        
        print("\nTeam Scores:")
        print(tabulate(data, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--scores":
        view_team_scores()
    else:
        view_questions() 