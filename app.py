import streamlit as st
from PIL import Image
import json

import sys
sys.path.append(r'C:\Users\devanshi\AppData\Roaming\Python\Python313\site-packages')

import pytesseract

from insights.match_insights import (
    detect_match_graph_type_from_image,
    summarize_manhattan,
    summarize_worm,
    summarize_run_rate,
    summarize_wickets_pie,
    summarize_partnership,
    summarize_types_of_runs,
)

from insights.player_insights import (
    detect_player_graph_type_from_image,
    summarize_player_current_form,
    summarize_player_playing_style,
    summarize_shot_analysis_runs,
    summarize_shot_analysis_outs,
    summarize_player_wagon_wheel,
    summarize_batting_position,
    summarize_player_run_types,
    summarize_vs_bowling_type,
)

from insights.team_insights import(
    detect_team_graph_type_from_image,
    summarize_team_current_form,
    summarize_team_toss_insights,
)

st.set_page_config(page_title="Cricket Graph Explainer", layout="centered")

st.title("🏏 Cricket Graph Explainer")
st.write("Upload a cricket graph (Manhattan, Worm, or Run Rate) to get a summary.")



def detect_graph_category_from_image(image):
    try:
        text = pytesseract.image_to_string(image).lower()
        if any(kw in text for kw in ["type of runs"]):  # singular
            return "match"
        elif any(kw in text for kw in ["types of runs"]):  # plural
            return "player"
        
        elif any(kw in text for kw in ["current form"]):
            if any(kw in text for kw in ["score"]) or any(kw in text for kw in ["out type"]):
                 return "player"
            else:
                return "team"
            
        elif any(kw in text for kw in ["manhattan", "worm", "run rate", "partnership", "wickets pie"]):
            return "match"
        elif any(kw in text for kw in ["playing style", "wagon wheel", "shots analysis", "batting position", "bowling type"]):
            return "player"
        elif any(kw in text for kw in ["toss insights", "win toss", "bat first", "field first"]):
            return "team"
    except Exception as e:
        print("Category detection failed:", e)

    return "unknown"


# --- Upload Section ---
uploaded_file = st.file_uploader("Upload a graph image", type=["png", "jpg", "jpeg"])
json_file = st.file_uploader("Upload match JSON file", type=["json"])

match_data = None
if json_file is not None:
    try:
        match_data = json.load(json_file)
        st.success("Match data loaded successfully!")
    except Exception as e:
        st.error(f"Error loading JSON: {e}")

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Graph", use_container_width=True)
    
    # 🧠 New step: Detect graph category
    category = detect_graph_category_from_image(image)
    st.markdown(f"### 📂 Detected Category: **{category.capitalize()} Insight**")
    if category == "match":
        graph_type = detect_match_graph_type_from_image(image)
        st.markdown(f"### 📝 Detected Graph Type: **{graph_type}**")

        if graph_type == "Manhattan":
            summarize_manhattan(match_data)
        elif graph_type == "Worm":
            summarize_worm(match_data)
        elif graph_type == "Run Rate":
            summarize_run_rate(match_data)
        elif graph_type == "Wickets Pie":
            summarize_wickets_pie(match_data)
        elif graph_type == "Partnership":
            summarize_partnership(match_data)
        elif graph_type == "Types of Runs":
            summarize_types_of_runs(match_data)
        else:
            st.error("❌ Could not identify match graph type.")

    elif category == "player":
        if match_data is not None:
            player_graph_type = detect_player_graph_type_from_image(image)
            if player_graph_type:
                st.markdown(f"### 📝 Detected Player Graph: **{player_graph_type.replace('_', ' ').title()}**")
                if player_graph_type == "player_current_form":
                    summarize_player_current_form(match_data["data"])
                elif  player_graph_type == "player_playing_style":
                    summarize_player_playing_style(match_data["data"])
                elif player_graph_type == "player_wagon_wheel":
                    summarize_player_wagon_wheel(match_data["data"])
                elif player_graph_type == "player_shot_analysis_runs":
                    summarize_shot_analysis_runs(match_data["data"])
                elif player_graph_type == "player_shot_analysis_outs":
                    summarize_shot_analysis_outs(match_data["data"])
                elif player_graph_type =="player_position":
                    summarize_batting_position(match_data["data"])
                elif player_graph_type =="player_vs_bowling":
                    summarize_vs_bowling_type(match_data["data"])
                elif player_graph_type =="player_run_types":
                    summarize_player_run_types(match_data["data"])
                else:
                    st.error("❌ Could not identify match graph type.")
                
            else:
                st.warning("⚠️ Could not detect player graph type from uploaded JSON.")
        else:
            st.warning("📄 Please upload a player JSON file to continue.")

    elif category == "team":
            if match_data is not None:
                team_graph_type = detect_team_graph_type_from_image(image)
                if team_graph_type:
                    st.markdown(f"### 🧢 Detected Team Graph: **{team_graph_type.replace('_', ' ').title()}**")
                    if team_graph_type == "team_current_form":
                        summarize_team_current_form(match_data["data"])
                    elif team_graph_type == "team_toss_insights":
                        summarize_team_toss_insights(match_data["data"])
                    else:
                        st.warning("⚠️ Team graph type not supported yet.")
                else:
                    st.warning("⚠️ Could not detect team graph type from image.")
            else:
                st.warning("📄 Please upload a team JSON file to continue.")



