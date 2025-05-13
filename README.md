# Panel Showdown

A lightweight Streamlit app for running live panel "battle" sessions between Business Central and Finance & Operations consultants. The app provides three different views for audience members, moderators, and display purposes.

## Features

- **Audience View**: Submit questions and vote on panelists
- **Moderator View**: Control active questions, manage the queue, and reset votes
- **Display View**: Show current question and team scores on the big screen
- Real-time updates across all views
- Simple JSON-based state management
- Clean, modern UI with responsive design

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
2. Use the sidebar to switch between views:
   - **Audience**: Submit questions and vote
   - **Moderator**: Manage questions and control the session
   - **Display**: Show on the big screen

### Audience View
- Submit questions using the form at the top
- Vote for questions using the BC/FO buttons
- See all submitted questions and their current votes

### Moderator View
- Set the active question
- Remove inappropriate questions
- Reset votes when needed
- Monitor the session progress

### Display View
- Shows current team scores
- Displays the active question
- Auto-refreshes to stay current
- Perfect for displaying on a projector or large screen

## State Management

The app uses a simple JSON file (`panel_state.json`) to maintain state across all views. This file is automatically created when the app starts and is updated in real-time as users interact with the app.

## Contributing

Feel free to submit issues and enhancement requests!