def generate_feedback(analysis):
    """
    analysis = {
        "timeline": [...],
        "top_positions": [...],
        "distribution": {...}
    }
    """

    feedback = []

    segments = analysis.get("timeline", [])
    top_positions = analysis.get("top_positions", [])
    distribution = analysis.get("distribution", {})

    if not segments or not distribution:
        return ["No significant positions detected."]

    # -----------------------------
    # Dominant Position
    # -----------------------------
    dominant_position, dominant_percent = top_positions[0]

    feedback.append(
        f"Your dominant position was {dominant_position.replace('_', ' ')} "
        f"({dominant_percent}% of the round)."
    )

    # -----------------------------
    # Top 3 Breakdown
    # -----------------------------
    if len(top_positions) > 1:
        second_position, second_percent = top_positions[1]
        feedback.append(
            f"You also spent significant time in {second_position.replace('_',' ')} "
            f"({second_percent}%)."
        )

    if len(top_positions) > 2:
        third_position, third_percent = top_positions[2]
        feedback.append(
            f"{third_position.replace('_',' ')} appeared regularly "
            f"({third_percent}%)."
        )

    # -----------------------------
    # Positional Insights
    # -----------------------------
    aggressive_positions = {"mount", "back", "side_control"}

    aggressive_time = sum(
        distribution.get(pos, 0) for pos in aggressive_positions
    )

    if aggressive_time > 30:
        feedback.append(
            "You maintained strong offensive control for much of the round."
        )
    elif aggressive_time < 10:
        feedback.append(
            "Consider working toward more dominant top positions."
        )

    if distribution.get("turtle", 0) > 20:
        feedback.append(
            "You spent considerable time in turtle. Focus on faster escapes or recovery transitions."
        )

    guard_positions = {"open_guard", "closed_guard", "half_guard", "5050_guard"}

    guard_time = sum(
        distribution.get(pos, 0) for pos in guard_positions
    )

    if guard_time > 50:
        feedback.append(
            "This round was guard-dominant. Work on sweeps or transitions to top control."
        )

    if distribution.get("standing", 0) > 15:
        feedback.append(
            "Significant standing engagement detected. Takedown chains could improve control time."
        )

    avg_segment_length = sum(
        (s["end_s"] - s["start_s"]) for s in segments
    ) / len(segments)

    if avg_segment_length < 3:
        feedback.append(
            "Frequent transitions detected. Improving positional control stability may increase dominance."
        )

    return feedback