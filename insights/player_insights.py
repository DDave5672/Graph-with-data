import pytesseract
from collections import defaultdict
import streamlit as st
from datetime import datetime

import pytesseract
import re

def detect_player_graph_type_from_image(image):
    try:
        text = pytesseract.image_to_string(image).lower()

        # Count occurrences of relevant keywords
        runs_count = len(re.findall(r"\bruns?\b", text))
        outs_count = len(re.findall(r"\b(out|outs|wickets)\b", text))

        if "types of runs" in text:
            return "player_run_types"
        
        elif "shot" in text and "analysis" in text:
            if runs_count > outs_count:
                return "player_shot_analysis_runs"
            elif outs_count > runs_count:
                return "player_shot_analysis_outs"
            else:
                return "player_shot_analysis_unknown"

        elif "current form" in text:
            return "player_current_form"
        elif "playing style" in text:
            return "player_playing_style"
        elif "wagon wheel" in text:
            return "player_wagon_wheel"
        elif "batting position" in text:
            return "player_position"
        elif "bowling type" in text:
            return "player_vs_bowling"

    except Exception as e:
        print("OCR failed:", e)

    return None

def summarize_player_current_form(data):
    matches = data.get("current_form_graph_data", [])
    if not matches:
        st.warning("No current form data found.")
        return

    total_runs = sum(m["runs"] for m in matches)
    total_balls = sum(m["balls"] for m in matches)
    innings = len(matches)
    outs = sum(1 for m in matches if m.get("is_out", 0) == 1)
    dismissals = [m.get("out_type") for m in matches if m.get("is_out", 0) == 1 and m.get("out_type")]

    avg = total_runs / outs if outs else total_runs
    sr = (total_runs / total_balls * 100) if total_balls else 0

    top_score = max(matches, key=lambda x: x["runs"])
    dismissal_freq = max(set(dismissals), key=dismissals.count) if dismissals else None

    lines = [
        f"📈 Over the last **{innings} innings**, the batsman scored **{total_runs} runs** at an average of **{avg:.2f}** and a strike rate of **{sr:.2f}**.",
        f"Highest score was **{top_score['runs']} ({top_score['balls']} balls)**",
    ]

    if dismissal_freq:
        lines.append(f"and the most common dismissal was **{dismissal_freq}**.")

    st.success("\n".join(lines))

import streamlit as st

def summarize_player_playing_style(data):
    graph_data = data.get("playing_style_graph_data", {}).get("all", [])
    if not graph_data:
        st.warning("No playing style data found.")
        return

    total_runs = sum(int(d["runs"]) for d in graph_data)
    total_balls = len(graph_data)
    sr = float(graph_data[-1]["SR"]) if graph_data else 0

    # Check acceleration pattern
    first5 = sum(int(d["runs"]) for d in graph_data[:5])
    last5 = sum(int(d["runs"]) for d in graph_data[-5:])
    intent = "accelerates later" if last5 > first5 else "starts strong"

    summary = (
        f"🧪 The batsman has scored **{total_runs} runs in {total_balls} balls**, maintaining a strike rate of **{sr:.2f}**.\n\n"
        f"⚡ Based on run trends, the player **{intent}**."
    )

    st.success(summary)


def summarize_player_wagon_wheel(data):
    try:
        entries = data.get("wagon_wheel_graph_data", [])
        if not entries:
            st.warning("No wagon wheel data available.")
            return

        from collections import defaultdict, Counter

        region_runs = defaultdict(int)
        bowler_type_counter = Counter()

        for entry in entries:
            run = int(entry.get("run", 0))
            region = entry.get("wagon_part")
            bowling_type = entry.get("bowling_type_name", "Unknown")

            if region:
                region_runs[region] += run
            bowler_type_counter[bowling_type] += run

        if not region_runs:
            st.warning("No valid region data found.")
            return

        # Map region number to readable fielding position
        region_names = {
            "1": "Mid-wicket",
            "2": "Mid-on",
            "3": "Mid-off",
            "4": "Cover",
            "5": "Point",
            "6": "Square leg"
        }

        best_region = max(region_runs.items(), key=lambda x: x[1])[0]
        zone_name = region_names.get(best_region, f"Region {best_region}")
        zone_runs = region_runs[best_region]
        productive_bowler = bowler_type_counter.most_common(1)[0][0]

        summary = (
            f"🔍 The batsman has been most effective in the **{zone_name}** region, scoring **{zone_runs} runs** there. "
            f"Placing a strong fielder in that zone could help restrict scoring. "
            f"They’ve also been particularly productive against **{productive_bowler}** bowlers, "
            f"so adjusting your attack strategy accordingly might reduce their impact."
        )

        st.success(summary)
    except Exception as e:
        st.error(f"❌ Error processing wagon wheel data: {e}")



def summarize_shot_analysis_runs(data):
    shots = data.get("shot_runs_graph_data", [])
    if not shots:
        st.warning("No shot analysis (runs) data found.")
        return

    top_shots = sorted(shots, key=lambda x: x["runs"], reverse=True)[:3]

    lines = [f"🏏 The batsman’s most productive shot is **{top_shots[0]['shot_name']}**, fetching **{top_shots[0]['runs']} runs**."]
    if len(top_shots) > 1:
        for shot in top_shots[1:]:
            lines.append(f"• They’ve also done well with the **{shot['shot_name']}** ({shot['runs']} runs).")

    lines.append("🧠 Consider defending these areas heavily — they’re the batsman's strongest scoring options.")
    st.success("\n".join(lines))

import streamlit as st

def summarize_shot_analysis_runs(data):
    shots = data.get("shot_runs_graph_data", [])
    if not shots:
        st.warning("No shot analysis (runs) data found.")
        return

    # Sort by most runs scored from a shot
    top_shots = sorted(shots, key=lambda x: x.get("runs", 0), reverse=True)[:3]

    lines = [f"🏏 The batsman’s most productive shot is **{top_shots[0]['shot_name']}**, fetching **{top_shots[0]['runs']} runs**."]
    
    if len(top_shots) > 1:
        for shot in top_shots[1:]:
            lines.append(f"• They've also scored well with the **{shot['shot_name']}** ({shot['runs']} runs).")

    lines.append("🧠 These shots define the batsman’s scoring style — protect those zones with deep fielders.")
    st.success("\n".join(lines))

import streamlit as st

def summarize_shot_analysis_outs(data):
    shots = data.get("shot_outs_graph_data", [])
    if not shots:
        st.warning("No shot analysis (outs) data found.")
        return

    most_dismissed = max(shots, key=lambda x: x["outs"])
    shot = most_dismissed["shot_name"]
    outs = most_dismissed["outs"]

    summary = (
        f"🚨 The batsman has been dismissed most often while playing the **{shot}**, getting out **{outs} times**.\n\n"
        f"🧠 Consider encouraging this shot with specific field placements or slower deliveries — it's their weak spot."
    )
    st.success(summary)

import streamlit as st

def summarize_batting_position(data):
    graph = data.get("batting_position_graph_data", {}).get("all", [])
    statements = {s["text"]: s["value"] for s in data.get("statements", [])}

    if not graph:
        st.warning("No batting position data found.")
        return

    # Find best actual performance by runs
    top_by_runs = max(graph, key=lambda x: x.get("runs", 0))
    top_position = top_by_runs["position"]
    runs = top_by_runs["runs"]
    avg = float(top_by_runs["avg"])
    sr = float(top_by_runs["SR"])
    innings = top_by_runs["total_match"]

    # Preferable position (from statements, not stats)
    pref_1 = statements.get("Preferable batting position for Viswajitsinh Rathod")
    pref_2 = statements.get("2nd preferable batting position for Viswajitsinh Rathod")

    summary = (
        f"🧠 The batsman’s most productive position is **#{top_position}**, where they've scored **{runs} runs** "
        f"at an average of **{avg:.2f}** and a strike rate of **{sr:.2f}** across **{innings} innings**.\n\n"
    )

    if pref_1 and pref_2:
        summary += (
            f"📌 According to data preference, position **#{pref_1}** is most suitable, "
            f"followed by **#{pref_2}**. These likely match the batsman's comfort and success rate."
        )

    st.success(summary.strip())

import streamlit as st

def summarize_vs_bowling_type(data):
    rows = data.get("graph_data", [])
    if not rows:
        st.warning("No data found for bowling type performance.")
        return

    # Convert string values to floats
    for r in rows:
        r["avg"] = float(r.get("average", 0))
        r["sr"] = float(r.get("strike_rate", 0))
        r["wk"] = float(r.get("wicket", "0").replace("%", ""))

    # Best: highest average (if SR is close), worst: highest dismissal rate
    best_type = max(rows, key=lambda r: r["avg"])
    weak_type = max(rows, key=lambda r: r["wk"])

    summary = (
        f"📊 The batsman performs best against **{best_type['bowling_type']}**, "
        f"scoring an average of **{best_type['avg']}** and a strike rate of **{best_type['sr']}**.\n\n"
        f"⚠️ On the other hand, they've struggled most against **{weak_type['bowling_type']}**, "
        f"where their dismissal rate is **{weak_type['wk']}%** — the highest among all bowling types."
    )

    st.success(summary)

import streamlit as st

def summarize_player_run_types(data):
    rows = data.get("types_of_runs_graph_data", [])
    if not rows:
        st.warning("No types of runs data found.")
        return

    # Filter out empty bowling types
    valid_rows = [r for r in rows if r.get("bowling_type_name") and r.get("total_runs", 0) > 0]

    # Most dot balls (pressure bowling)
    dotty = max(valid_rows, key=lambda r: r.get("dot_balls", 0))
    dot_type = dotty["bowling_type_name"]
    dot_rate = dotty["per_dot_balls"]

    # Most boundary runs (aggressive scoring)
    boundary = max(valid_rows, key=lambda r: r.get("boundaries_run", 0))
    b_type = boundary["bowling_type_name"]
    b_runs = boundary["boundaries_run"]
    b_total = boundary["total_runs"]
    boundary_pct = (b_runs / b_total * 100) if b_total else 0

    summary = (
        f"🧱 The batsman plays the most dot balls against **{dot_type}** bowlers — "
        f"with **{dot_rate:.1f}%** of deliveries not scoring.\n\n"
        f"🚀 However, they're highly aggressive against **{b_type}**, scoring **{b_runs} out of {b_total} runs** "
        f"via boundaries — that's **{boundary_pct:.1f}%** of their output.\n\n"
        f"📌 Consider using {dot_type} options early to build pressure, then rotate away from {b_type} when they're set."
    )

    st.success(summary)
