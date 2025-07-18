import pytesseract
from collections import defaultdict
import streamlit as st
from datetime import datetime

def detect_team_graph_type_from_image(image):
    try:
        text = pytesseract.image_to_string(image).lower()

        if "current form" in text or ("current form" in text and "result" in text):
            return "team_current_form"
        elif any(kw in text for kw in ["toss insights", "win toss", "bat first", "field first"]):
            return "team_toss_insights"

    except Exception as e:
        print("OCR failed for team graph:", e)

    return None

def summarize_team_current_form(data):
    matches = data.get("graph_data", [])
    if not matches:
        st.warning("No match data available for team current form.")
        return

    team_name = matches[0].get("team_name", "This team")
    total = len(matches)
    team_id = data.get("team_id", 2509267)
    wins = 0
    losses = 0
    abandoned = 0
    win_margins = []

    for match in matches:
        result = match.get("match_result", "").lower()
        if result == "abandoned":
            abandoned += 1
        elif result == "resulted":
            if match.get("won_team_id") == team_id:
                wins += 1
                win_by = match.get("win_by", "")
                if win_by:
                    win_margins.append(win_by)
            else:
                losses += 1

    summary = (
        f"📊 **{team_name}** has played their last **{total} matches** with "
        f"**{wins} wins**, **{losses} losses**, and **{abandoned} abandoned**.\n\n"
    )

    if wins > losses:
        summary += "🟢 They’ve had a strong recent run, dominating most opponents."
    elif losses > wins:
        summary += "🔴 They've been struggling lately with more losses than wins."
    else:
        summary += "🟡 Their form has been balanced, with mixed outcomes."

    if win_margins:
        summary += f"\n\n🚀 Biggest win: **{max(win_margins, key=lambda s: len(s))}**."

    st.success(summary.strip())

import streamlit as st

def summarize_team_toss_insights(data):
    d = data.get("graph_data", {})
    if not d:
        st.warning("No toss insights data found.")
        return

    team = d.get("team_name", "This team")
    toss_won = d.get("won_toss", 0)
    toss_lost = d.get("lost_toss", 0)
    bat_first = d.get("bat_first", 0)
    field_first = d.get("field_first", 0)
    won_bat = d.get("won_bat_first", 0)
    won_field = d.get("won_field_first", 0)

    summary = (
        f"🧢 **{team}** has won the toss **{toss_won}** times and lost it **{toss_lost}** times in their last few matches.\n\n"
        f"📌 When winning the toss, they chose to **bat first {bat_first} times** "
        f"(won {won_bat}), and **field first {field_first} times** (won {won_field}).\n\n"
    )

    if won_bat > won_field:
        summary += "🟢 They have clearly performed better when batting first after winning the toss."
    elif won_field > won_bat:
        summary += "🔵 They’ve had better luck chasing after winning the toss."
    else:
        summary += "🟡 Their toss outcomes show no strong preference between batting or fielding first."

    st.success(summary.strip())
