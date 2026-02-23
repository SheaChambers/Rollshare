def generate_feedback(segments):
    feedback = []

    # Remove micro segments (< 2 seconds)
    segments = [s for s in segments if (s["end_s"] - s["start_s"]) > 2]

    if not segments:
        return ["No significant positions detected."]

    # Dominant position
    durations = {}
    for s in segments:
        duration = s["end_s"] - s["start_s"]
        durations[s["position"]] = durations.get(s["position"], 0) + duration

    dominant = max(durations.items(), key=lambda x: x[1])[0]

    feedback.append(f"Your dominant position was {dominant.replace('_',' ')}.")

    # Transition feedback
    positions = [s["position"] for s in segments]

    if "takedown" in positions:
        feedback.append("A takedown transition was detected. Consider improving level change timing.")

    if "mount" in positions:
        feedback.append("You achieved mount. Focus on hip pressure and base stability.")

    if "back" in positions:
        feedback.append("Back control detected. Maintain chest-to-back connection.")

    if "open_guard" in positions:
        feedback.append("Open guard used frequently. Work on angle creation and leg control.")

    return feedback