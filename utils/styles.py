import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        /* Button styles */
        .stButton>button {
            width: 100%;
        }

        /* Question card styles */
        .question-card {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 0.5rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            border: 1px solid #e0e0e0;
        }
        .active-question {
            background-color: #ffffff;
            border: 3px solid #0066cc;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .past-question {
            background-color: #f8f9fa;
            border: 1px solid #dee2e6;
            opacity: 0.9;
            margin: 1rem auto;
            max-width: 900px;
            padding: 1.5rem;
            border-radius: 0.5rem;
            text-align: center;
            font-size: 1.5rem;
            color: #666;
        }
        .past-question:hover {
            opacity: 1;
        }

        /* Score display styles */
        .score-display {
            font-size: 2.5rem;
            font-weight: bold;
            text-align: center;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .bc-score {
            background-color: #e6f3ff;
            color: #0066cc;
            border: 2px solid #0066cc;
        }
        .fo-score {
            background-color: #fff0f0;
            color: #cc0000;
            border: 2px solid #cc0000;
        }

        /* Panelist card styles */
        .panelist-card {
            background-color: #ffffff;
            padding: 1.5rem;
            border-radius: 0.5rem;
            text-align: center;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
            display: inline-block;
            width: 100%;
        }
        .panelist-image {
            width: 200px;
            height: 200px;
            object-fit: cover;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            display: block;
            margin-left: auto;
            margin-right: auto;
        }
        .team-bc {
            border: 3px solid #0066cc;
        }
        .team-fo {
            border: 3px solid #cc0000;
        }

        /* Question text and meta styles */
        .question-text {
            color: #000000 !important;
            font-size: 1.5rem;
            margin-bottom: 1rem;
            line-height: 1.4;
        }
        .question-meta {
            color: #666666 !important;
            font-size: 0.9rem;
            line-height: 1.4;
        }

        /* Layout styles */
        .stContainer {
            padding: 1rem 0;
        }
        [data-testid="column"] {
            padding: 0 1rem;
        }

        /* Display view specific styles */
        #root > div:nth-child(1) > div > div > div > div > section > div {
            padding-top: 0rem;
        }
        .stDeployButton {
            display: none;
        }
        footer {
            visibility: hidden;
        }
        </style>
    """, unsafe_allow_html=True) 