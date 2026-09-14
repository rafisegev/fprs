
def star_rating_and_label(final_score):
    if final_score >= 90: return "⭐⭐⭐⭐⭐", "Top 10% – ביצועים מעולים, אלפא גבוהה, ללא דעיכה"
    elif final_score >= 67.5: return "⭐⭐⭐⭐", "Top 22.5% – איכות גבוהה"
    elif final_score >= 32.5: return "⭐⭐⭐", "Middle 35% – ביצועים ממוצעים"
    elif final_score >= 10: return "⭐⭐", "Bottom 22.5% – עמלות גבוהות / תחילת דעיכה"
    else: return "⭐", "Bottom 10% – פיגור חריף"
def quality_system_label(final_score):
    if final_score >= 90: return "מצוינת"
    if final_score >= 75: return "טובה מאוד"
    if final_score >= 50: return "ממוצעת"
    if final_score >= 25: return "נמוכה"
    return "חלשה"
