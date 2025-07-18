import pytesseract
from collections import defaultdict
import streamlit as st


def detect_match_graph_type_from_image(image):
    try:
        text = pytesseract.image_to_string(image).lower()
        text = text.replace("\n", " ").replace("\t", " ").strip()

        if any(kw in text for kw in ["run rate", "runrate", "rr", "rpo"]):
            return "Run Rate"
        elif any(kw in text for kw in ["manhattan", "runs per over", "run distribution", "per over runs"]):
            return "Manhattan"
        elif any(kw in text for kw in ["worm", "cumulative runs", "cumulative", "score progress"]):
            return "Worm"
        elif any(kw in text for kw in ["wickets pie", "dismissals", "dismissal type", "fall of wicket"]):
            return "Wickets Pie"
        elif "partnership" in text:
            return "Partnership"
        elif any(kw in text for kw in ["type of runs"]):  # match only
            return "Types of Runs"

    except Exception as e:
        print("OCR failed:", e)

    return None


def summarize_manhattan(match_data):
    team_overs = {}
    for inning in match_data["innings"]:
        team = inning["team"]
        runs_by_over = []
        for over in inning["overs"]:
            total_runs = sum(delivery["runs"]["total"] for delivery in over["deliveries"])
            runs_by_over.append(total_runs)
        team_overs[team] = runs_by_over

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

    if len(summary_parts) == 2:
        team1_summary = summary_parts[0].rstrip(".")
        team2_summary = summary_parts[1]
        team2_summary = team2_summary[0].lower() + team2_summary[1:]
        combined_summary = f"{team1_summary}, Whereas {team2_summary}"
        st.success(combined_summary)
    else:
        for s in summary_parts:
            st.success(s)


def summarize_worm(match_data):
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

    team_names = list(worm_data.keys())
    if len(team_names) == 2:
        team1, team2 = team_names
        team1_runs = worm_data[team1]
        team2_runs = worm_data[team2]
        turning_point = next((i+1 for i, (r1, r2) in enumerate(zip(team1_runs, team2_runs)) if r1 - r2 > 10), None)
        winner = team1 if team1_runs[-1] > team2_runs[-1] else team2
        summary = f"{team1} and {team2} were neck and neck for most of the innings. "
        if turning_point:
            summary += f"{winner} pulled ahead noticeably after over {turning_point}. "
        summary += f"{winner} maintained their lead and finished stronger."
        st.success(summary)
    else:
        st.warning("Expected two teams in the data.")


def summarize_run_rate(match_data):
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

    if len(summary_parts) == 2:
        team1_summary = summary_parts[0].rstrip(".")
        team2_summary = summary_parts[1]
        team2_summary = team2_summary[0].lower() + team2_summary[1:]
        combined_summary = f"{team1_summary}, and {team2_summary}"
        st.success(combined_summary)


def summarize_wickets_pie(match_data):
    wicket_data = {}
    for inning in match_data["innings"]:
        for over in inning["overs"]:
            for delivery in over["deliveries"]:
                if "wickets" in delivery:
                    for w in delivery["wickets"]:
                        kind = w["kind"]
                        wicket_data[kind] = wicket_data.get(kind, 0) + 1

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


def summarize_partnership(match_data):
    partnerships = defaultdict(int)

    for inning in match_data["innings"]:
        for over in inning["overs"]:
            for delivery in over["deliveries"]:
                batter = delivery["batter"]
                non_striker = delivery["non_striker"]
                runs = delivery["runs"]["total"]
                pair = tuple(sorted([batter, non_striker]))
                partnerships[pair] += runs

    sorted_partnerships = sorted(partnerships.items(), key=lambda x: x[1], reverse=True)[:3]

    if sorted_partnerships:
        main = sorted_partnerships[0]
        summary = f"The highest partnership was between **{main[0][0]}** and **{main[0][1]}**, who added **{main[1]} runs**."

        for pair, runs in sorted_partnerships[1:]:
            summary += f" Another key stand was **{pair[0]}** and **{pair[1]}**, adding **{runs} runs**."
        st.success(summary)
    else:
        st.info("No partnerships found in the data.")


def summarize_types_of_runs(match_data):
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
