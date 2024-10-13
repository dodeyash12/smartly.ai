import streamlit as st
from streamlit_calendar import calendar
from datetime import datetime, timedelta
st.set_page_config(layout="wide")
from trail import study_schedule
# Study schedule data
# Create a dictionary to hold daily study sessions
daily_study_sessions = {}

# Process study dates for each assignment
for assignment_title, details in study_schedule.items():
    for study in details['study_dates']:
        date_str = study['date']
        hours = study['hours']
        # Initialize list if date not in dictionary
        if date_str not in daily_study_sessions:
            daily_study_sessions[date_str] = []
        # Append study session
        daily_study_sessions[date_str].append({
            'assignment_title': assignment_title,
            'hours': hours
        })

# Generate events for the calendar
events = []

# Colors for different event types
study_color = 'blue'
due_date_color = 'red'

for date_str in sorted(daily_study_sessions.keys()):
    study_sessions = daily_study_sessions[date_str]
    # Start scheduling from 9:00 AM
    current_time = datetime.strptime(date_str + " 09:00", "%Y-%m-%d %H:%M")
    for session in study_sessions:
        assignment_title = session['assignment_title']
        hours = session['hours']
        start_time = current_time
        end_time = start_time + timedelta(hours=hours)
        # Create study session event
        event = {
            'title': f"Study for {assignment_title}",
            'start': start_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'end': end_time.strftime("%Y-%m-%dT%H:%M:%S"),
            'color': study_color
        }
        events.append(event)
        # Update current time for next session
        current_time = end_time

# Generate events for due dates
for assignment_title, details in study_schedule.items():
    due_date_str = details['due_date']
    # Create due date event as an all-day event
    event = {
        'title': f"{assignment_title} Due",
        'start': due_date_str,
        'end': due_date_str,
        'color': due_date_color,
        'allDay': True
    }
    events.append(event)

# Calendar options
calendar_options = {
    "initialView": "timeGridWeek",
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay"
    },
    "slotMinTime": "06:00:00",
    "slotMaxTime": "22:00:00",
    "allDaySlot": True  # Enable all-day slot to show due dates
}

# Custom CSS to adjust event appearance
custom_css = """
    .fc-event {
        font-size: 0.8em;
    }
    .fc-event-title {
        white-space: normal;
    }
"""

# Display the calendar using Streamlit
st.title("Study Schedule Calendar")

calendar_component = calendar(
    events=events,
    options=calendar_options,
    custom_css=custom_css,
    key="calendar"
)

st.write(calendar_component)
