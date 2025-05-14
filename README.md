# Panel Showdown

A lightweight Streamlit app for running live panel "battle" sessions between Business Central and Finance & Operations consultants. The app provides three different views for audience members, moderators, and display purposes, with real-time updates and a modern, responsive interface.

## Features

- **Audience View**
  - Submit questions with author attribution
  - Vote for Business Central or Finance & Operations teams
  - View current and past questions with voting status
  - Real-time updates of questions and votes
  - QR code for easy access to the audience view

- **Moderator View**
  - Control active questions and manage the question queue
  - Award points to teams for winning questions
  - Reset votes and questions when needed
  - Load initial questions from a JSON file
  - Toggle score visibility (blur/unblur)
  - Monitor session progress and team scores

- **Display View**
  - Show current active question with voting progress
  - Display team scores with optional blur effect
  - Show panelist information
  - Auto-refresh to stay current
  - Clean, distraction-free interface for projector display
  - Past questions history

## Technical Details

- Built with Streamlit for a modern, responsive web interface
- SQLite database for reliable state management
- Real-time updates across all views
- Secure access control for moderator and display views
- Custom styling for optimal viewing experience
- QR code generation for easy audience access

## Setup

1. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the app:
   ```bash
   streamlit run app.py
   ```

## Usage

1. Open the app in your browser (default: http://localhost:8501)
2. Access different views using URL parameters:
   - Audience view: `http://localhost:8501/?view=audience`
   - Moderator view: `http://localhost:8501/?view=moderator&access=moderator`
   - Display view: `http://localhost:8501/?view=display&access=display`

### Audience View
- Submit questions using the form at the top
- Vote for questions using the BC/FO buttons
- See all submitted questions and their current votes
- Track your voting history
- Scan QR code to join the session

### Moderator View
- Set and manage active questions
- Award points to teams
- Reset votes or questions when needed
- Load initial questions from JSON
- Toggle score visibility
- Monitor team progress

### Display View
- Shows current team scores (with optional blur)
- Displays the active question with voting progress
- Shows panelist information
- Auto-refreshes to stay current
- Clean interface optimized for projector display

## Database

The app uses SQLite for state management with the following features:
- Persistent storage of questions, votes, and team scores
- Individual vote tracking to prevent duplicate votes
- Automatic state synchronization across all views
- Backup and restore capabilities

## Contributing

Feel free to submit issues and enhancement requests! When contributing, please ensure you:
1. Follow the existing code style
2. Add appropriate tests for new features
3. Update the documentation as needed
4. Use meaningful commit messages

## License

This project is open source and available under the MIT License.