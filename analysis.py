def generate_analysis(income, expense):

    income = float(income)
    expense = float(expense)

    savings = income - expense

    # ---------- SCORE ----------
    if income <= 0:
        score = 0
    else:
        ratio = savings / income

        if ratio >= 0.50:
            score = 10
        elif ratio >= 0.40:
            score = 9
        elif ratio >= 0.30:
            score = 8
        elif ratio >= 0.20:
            score = 7
        elif ratio >= 0.10:
            score = 6
        elif ratio >= 0:
            score = 5
        elif ratio >= -0.10:
            score = 4
        elif ratio >= -0.20:
            score = 3
        elif ratio >= -0.30:
            score = 2
        else:
            score = 1

    # ---------- ALERT ----------
    if income == 0 and expense > 0:
        alert = "No income recorded yet."
    elif savings < 0:
        alert = "Warning: You are overspending."
    elif savings == 0:
        alert = "Your income and expense are equal."
    elif savings < income * 0.10:
        alert = "Low savings this month."
    elif savings < income * 0.30:
        alert = "Moderate savings. Can improve more."
    else:
        alert = "Excellent savings performance."

    # ---------- RECOMMENDATIONS ----------
    tips = []

    if income == 0:
        tips.append("Add your monthly income first.")
    if expense > income and income > 0:
        tips.append("Reduce unnecessary expenses immediately.")
    if expense > income * 0.70 and income > 0:
        tips.append("Spending is high. Review top categories.")
    if savings < income * 0.20 and income > 0:
        tips.append("Try saving at least 20% of income.")
    if savings > income * 0.30 and income > 0:
        tips.append("Great job. Consider investing savings.")
    if expense == 0 and income > 0:
        tips.append("No expenses added yet. Track spending regularly.")

    if not tips:
        tips.append("Maintain your current financial discipline.")

    return {
        "savings": round(savings, 2),
        "score": score,
        "alert": alert,
        "recommendations": tips
    }