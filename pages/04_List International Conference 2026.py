import streamlit as st

# Page configuration
st.set_page_config(page_title="2026 Conferences", layout="wide")

st.title("📅 International Conferences 2026")
st.markdown("Below is the list of upcoming Mechanical Engineering conferences for 2026.")

# Data structure
conferences = [
    {
        "Conference Name": "APCOMS-IMEC 2026",
        "Location": "Jakarta, Indonesia",
        "Dates": "Late 2026 (TBA)",
        "Link": "https://apcoms-imec.fti.trisakti.ac.id/",
        "Status": "Scopus Indexed"
    },
    {
        "Conference Name": "ICME 2026",
        "Location": "Johor, Malaysia",
        "Dates": "August 5 - 6, 2026",
        "Link": "https://conference.uthm.edu.my/index.php/icme/index",
        "Status": "Scopus Indexed"
    },
    {
        "Conference Name": "ASME IMECE 2026",
        "Location": "Vancouver, Canada",
        "Dates": "November 8 - 12, 2026",
        "Link": "https://www.asme.org/conferences-events/events/imece",
        "Status": "Scopus / WoS"
    },
    {
        "Conference Name": "Turbo Expo 2026",
        "Location": "Milan, Italy",
        "Dates": "June 15 - 19, 2026",
        "Link": "https://event.asme.org/Turbo-Expo",
        "Status": "Scopus / WoS"
    }
]

# Display as a clean table
st.table(conferences)

# Optional: Add a note about your current research focus
st.info("💡 Tip: Ensure your manuscript aligns with the 'Mechanical Engineering' or 'Automotive' tracks before submission.")
