import streamlit as st
from PIL import Image
import json 

st.set_page_config(page_title="Cricket Graph Explainer", layout="centered")

st.title("🏏 Cricket Graph Explainer")
st.write("Upload a cricket graph (Manhattan, Worm, or Run Rate) to get a summary.")


# Upload Section
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
    # Show the image
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Graph", use_container_width=True)

    # Step 2: Ask user to select graph type
    graph_type = st.selectbox(
    "What type of graph is this?",
    [
        "Select graph type",
        "Manhattan",
        "Worm",
        "Run Rate",
        "Wickets Pie",
        "Partnership",
        "Types of Runs"
    ]
)

    if graph_type != "Select graph type":
        st.markdown("### 📝 Summary")
        
        if graph_type == "Manhattan":
            st.markdown("#### 📊 Runs Per Over")

            if match_data is not None:
                team_overs = {}

                for inning in match_data["innings"]:
                    team = inning["team"]
                    runs_by_over = []

                    for over in inning["overs"]:
                        total_runs = sum(delivery["runs"]["total"] for delivery in over["deliveries"])
                        runs_by_over.append(total_runs)

                    team_overs[team] = runs_by_over

                # Create natural summaries
                summary_parts = []
                for team, overs in team_overs.items():
                    high_overs = [i + 1 for i, r in enumerate(overs) if r >= 15]
                    low_overs = [i + 1 for i, r in enumerate(overs) if r <= 5]
                    top_over = max(enumerate(overs, start=1), key=lambda x: x[1])

                    sentence = f"**{team}** had their highest scoring over in the {top_over[0]}th, smashing {top_over[1]} runs. "

                    if high_overs:
                        sentence += f"They had big momentum shifts in overs {', '.join(map(str, high_overs))}. "

                    if low_overs:
                        sentence += f"However, they slowed down significantly in overs {', '.join(map(str, low_overs))}. "

                    summary_parts.append(sentence)

                # Combine both summaries using "whereas" if there are 2 teams
                if len(summary_parts) == 2:
                    team1_summary = summary_parts[0].rstrip(".")
                    team2_summary = summary_parts[1]
                    team2_summary = team2_summary[0].lower() + team2_summary[1:]  # lowercase the start

                    combined_summary = f"{team1_summary}, Whereas {team2_summary}"
                    st.success(combined_summary)
                else:
                    for s in summary_parts:
                        st.markdown("### 📝 Summary")
                        st.success(s)

            else:
                st.warning("Please upload a match JSON file to show Manhattan chart summary.")

        elif graph_type == "Worm":
            st.markdown("#### 🪱 Cumulative Runs Over Time")

            if match_data is not None:
                worm_data = {}

                for inning in match_data["innings"]:
                    team = inning["team"]
                    cumulative_runs = []
                    total = 0

                    for over in inning["overs"]:
                        over_runs = sum(delivery["runs"]["total"] for delivery in over["deliveries"])
                        total += over_runs
                        cumulative_runs.append(total)

                    worm_data[team] = cumulative_runs
                # Simple comparison summary
                team_names = list(worm_data.keys())
                if len(team_names) == 2:
                    team1, team2 = team_names
                    team1_runs = worm_data[team1]
                    team2_runs = worm_data[team2]

                    # Find over where one team pulls ahead
                    turning_point = next((i+1 for i, (r1, r2) in enumerate(zip(team1_runs, team2_runs)) if r1 - r2 > 10), None)
                    winner = team1 if team1_runs[-1] > team2_runs[-1] else team2

                    summary = f"{team1} and {team2} were neck and neck for most of the innings. "
                    if turning_point:
                        summary += f"{winner} pulled ahead noticeably after over {turning_point}. "
                    summary += f"{winner} maintained their lead and finished stronger."
                    st.success(summary)
                else:
                    st.warning("Expected two teams in the data.")
            else:
                st.warning("Please upload a match JSON file to show Worm chart summary.")

        elif graph_type == "Run Rate":
            st.markdown("#### 📈 Run Rate Progression")

            if match_data is not None:
                run_rate_data = {}

                for inning in match_data["innings"]:
                    team = inning["team"]
                    cumulative_runs = 0
                    run_rates = []

                    for i, over in enumerate(inning["overs"]):
                        over_runs = sum(delivery["runs"]["total"] for delivery in over["deliveries"])
                        cumulative_runs += over_runs
                        current_over = i + 1
                        rr = round(cumulative_runs / current_over, 2)
                        run_rates.append(rr)

                    run_rate_data[team] = run_rates

                summary_parts = []
                # Generate summary
                for team, rates in run_rate_data.items():
                    trend = "steady" if max(rates) - min(rates) <= 2 else "up-and-down"
                    avg_rate = round(sum(rates) / len(rates), 2)
                    peak_over = rates.index(max(rates)) + 1
                    dip_over = rates.index(min(rates)) + 1

                    summary = (
                        f"**{team}** had a {trend} run rate overall. "
                        f"Their average run rate was {avg_rate}, "
                        f"peaking in over {peak_over} and dropping in over {dip_over}."
                    )

                    summary_parts.append(summary)
                # Combine using "whereas"
                if len(summary_parts) == 2:
                    team1_summary = summary_parts[0].rstrip(".")
                    team2_summary = summary_parts[1]
                    team2_summary = team2_summary[0].lower() + team2_summary[1:]

                    combined_summary = f"{team1_summary}, and {team2_summary}"
                    st.success(combined_summary)
            else:
                st.warning("Please upload a match JSON file to show Run Rate chart summary.")
        elif graph_type == "Wickets Pie":
            st.markdown("#### 📊 Wicket Breakdown")

            if match_data is not None:
                wicket_data = {}

                # Loop through both innings to count wicket types
                for inning in match_data["innings"]:
                    for over in inning["overs"]:
                        for delivery in over["deliveries"]:
                            if "wickets" in delivery:
                                for w in delivery["wickets"]:
                                    kind = w["kind"]
                                    wicket_data[kind] = wicket_data.get(kind, 0) + 1

                # Build summary
                if wicket_data:
                    most_common = max(wicket_data, key=wicket_data.get)
                    total_wickets = sum(wicket_data.values())
                    other_types = [k for k in wicket_data if k != most_common]

                    summary = (
                        f"A total of {total_wickets} wickets fell in this match. "
                        f"The most common dismissal was **{most_common}** ({wicket_data[most_common]} times)."
                    )

                    if other_types:
                        summary += " Other types included: " + ", ".join(other_types) + "."
                    st.success(summary)
                else:
                    st.info("No wickets found in the match data.")
            else:
                st.warning("Please upload a match JSON file to show real wicket data.")
        elif graph_type == "Partnership":
            st.markdown("#### 🤝 Partnership Summary")

            if match_data is not None:
                from collections import defaultdict

                partnerships = defaultdict(int)

                for inning in match_data["innings"]:
                    team = inning["team"]
                    current_pair = None
                    batter_on_strike = ""
                    non_striker = ""

                    for over in inning["overs"]:
                        for delivery in over["deliveries"]:
                            batter = delivery["batter"]
                            non_striker = delivery["non_striker"]
                            runs = delivery["runs"]["total"]

                            pair = tuple(sorted([batter, non_striker]))
                            partnerships[pair] += runs

                            # If there's a wicket, reset that pair
                            if "wickets" in delivery:
                                for w in delivery["wickets"]:
                                    if w["player_out"] in pair:
                                        # Break this partnership
                                        continue

                # Sort top 3 partnerships
                sorted_partnerships = sorted(partnerships.items(), key=lambda x: x[1], reverse=True)[:3]

                # Build summary
                if sorted_partnerships:
                    main = sorted_partnerships[0]
                    summary = f"The highest partnership was between **{main[0][0]}** and **{main[0][1]}**, who added **{main[1]} runs**."

                    for pair, runs in sorted_partnerships[1:]:
                        summary += f" Another key stand was **{pair[0]}** and **{pair[1]}**, adding **{runs} runs**."
                    st.success(summary)
                else:
                    st.info("No partnerships found in the data.")
            else:
                st.warning("Please upload a match JSON file to show partnership summary.")
        elif graph_type == "Types of Runs":
            st.markdown("#### 🧮 Types of Runs Summary")

            if match_data is not None:
                from collections import defaultdict

                run_type_summary = {}

                for inning in match_data["innings"]:
                    team = inning["team"]
                    run_types = defaultdict(int)

                    for over in inning["overs"]:
                        for delivery in over["deliveries"]:
                            if "runs" in delivery:
                                batted = delivery["runs"]["batter"]
                                if batted in [1, 2, 3, 4, 5, 6]:
                                    run_types[batted] += 1

                    run_type_summary[team] = dict(run_types)

                summary_parts = []

                for team, data in run_type_summary.items():
                    singles = data.get(1, 0)
                    doubles = data.get(2, 0)
                    triples = data.get(3, 0)
                    fours = data.get(4, 0)
                    sixes = data.get(6, 0)

                    sentence = (
                        f"**{team}** scored {singles} singles, {doubles} doubles"
                        f"{', ' + str(triples) + ' triples' if triples > 0 else ''}, "
                        f"hit {fours} fours and {sixes} sixes"
                    )

                    summary_parts.append(sentence)

                if len(summary_parts) == 2:
                    merged_summary = f"{summary_parts[0]}, and {summary_parts[1]}."
                    st.success(merged_summary)
                else:
                    for s in summary_parts:
                        st.success(s)

            else:
                st.warning("Please upload a match JSON file to show run type summary.")
