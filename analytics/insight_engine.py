def generate_insights(summary):
    """
    Intelligent Session Insights and Recommendations Engine.
    Analyzes session statistics to classify fatigue severity, interpret
    behavioral indicators, and select appropriate safety recommendations.
    
    Severity Classification Logic:
    - HIGH Severity: Peak fatigue score reaches or exceeds 40%, alert count is >= 5,
      or drowsiness (eyes closed) warnings exceed 5.
    - MEDIUM Severity: Peak fatigue is between 20% and 40%, alert count is >= 2,
      or yawning events/head tilt events exceed 3.
    - LOW Severity: Fatigue remains below 20% and no warning thresholds are crossed.
    """
    avg_fatigue = summary.get("average_fatigue", 0.0)
    peak_fatigue = summary.get("peak_fatigue", 0.0)
    drowsiness_events = summary.get("drowsiness_events", 0)
    yawn_events = summary.get("yawn_events", 0)
    tilt_events = summary.get("tilt_events", 0)
    duration = summary.get("duration", 0.0)
    alert_count = summary.get("alert_count", 0)
    
    # 1. Fatigue Severity Classification
    if peak_fatigue >= 40.0 or alert_count >= 5 or drowsiness_events >= 5:
        severity = "HIGH"
    elif peak_fatigue >= 20.0 or alert_count >= 2 or yawn_events >= 3 or tilt_events >= 3:
        severity = "MEDIUM"
    else:
        severity = "LOW"

    # 2. Fatigue Interpretation & Textual Summary
    summary_parts = []
    if severity == "HIGH":
        summary_parts.append(
            f"High fatigue detected during this {duration:.0f}-second session. "
            f"You experienced critical drowsiness indicators, peaking at {peak_fatigue:.1f}% fatigue. "
            f"Alert warnings triggered {alert_count} times, presenting a serious hazard of micro-sleeps."
        )
    elif severity == "MEDIUM":
        summary_parts.append(
            f"Moderate fatigue detected during this {duration:.0f}-second session. "
            f"Your fatigue levels peaked at {peak_fatigue:.1f}% with mild indicators. "
            f"Signs of secondary fatigue like yawning ({yawn_events}) or head tilting ({tilt_events}) were tracked."
        )
    else:
        summary_parts.append(
            f"Low fatigue detected during this {duration:.0f}-second session. "
            f"Your fatigue levels remained within safe parameters (peaking at {peak_fatigue:.1f}%), "
            f"demonstrating good alertness."
        )

    # 3. Actionable Recommendation Engine
    recommendations = []
    
    # Rest recommendations based on severity level
    if severity == "HIGH":
        recommendations.append("CRITICAL: Pull over safely immediately and take a 20-minute power nap.")
        recommendations.append("Avoid continuing to drive or perform focus-intensive tasks in this state.")
    elif severity == "MEDIUM":
        recommendations.append("Take a short break from driving or screens (10 to 15 minutes).")
        recommendations.append("Stretch your muscles, hydrate, or consume caffeine to boost alertness.")
    else:
        recommendations.append("Maintain your current pacing. Continue monitoring.")

    # Contextual triggers based on telemetry metrics
    if drowsiness_events > 0:
        recommendations.append("Rest your eyes to recover from screen/road glare and reduce eye fatigue.")
    if yawn_events >= 2:
        recommendations.append("Increase cabin airflow: Open windows or turn on the air conditioner to replenish oxygen levels.")
    if tilt_events >= 2:
        recommendations.append("Adjust your seating configuration and straighten posture to prevent nodding off.")
    if duration > 7200:  # 2 hours
        recommendations.append("You have monitored for over 2 hours. Take a mandatory safety rest break.")

    return {
        "severity": severity,
        "summary": " ".join(summary_parts),
        "recommendations": recommendations
    }
