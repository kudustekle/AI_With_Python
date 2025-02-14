from flask import Flask, render_template, request, jsonify
import re
from datetime import datetime, timedelta
from chatbot import chat_response
from database import get_repair_history, get_complaint_stats

app = Flask(__name__)

def parse_date_filter(user_input):
    today = datetime.today()
    date_filters = {
        "today": (today, today),
        "yesterday": (today - timedelta(days=1), today - timedelta(days=1)),
        "this week": (today - timedelta(days=today.weekday()), today),
        "last week": (today - timedelta(days=today.weekday() + 7), today - timedelta(days=today.weekday() + 1)),
        "this month": (datetime(today.year, today.month, 1), today),
        "last month": (datetime(today.year, today.month - 1, 1), datetime(today.year, today.month, 1) - timedelta(days=1)),
        "this year": (datetime(today.year, 1, 1), today),
        "last year": (datetime(today.year - 1, 1, 1), datetime(today.year - 1, 12, 31))
    }
    for key, value in date_filters.items():
        if key in user_input:
            return value
    return None

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.get_json()
        user_input = data.get("question", "").strip().lower()

        if user_input in ["hi", "hello", "hey", "howdy"]:
            return jsonify({"response": "Hello! How can I assist you today?"})

        phone_match = re.search(r"\b\d{6,10}\b", user_input)
        phone_number = phone_match.group(0) if phone_match else None

        year_match = re.search(r"\b\d{4}\b", user_input)
        year = int(year_match.group(0)) if year_match else None

        status_match = re.search(r"(complete|waiting list|uncomplete)", user_input)
        status_filter = status_match.group(0) if status_match else None

        date_range = parse_date_filter(user_input)

        if "how many" in user_input or "number of" in user_input:
            count = get_complaint_stats(date_range)
            return jsonify({"response": f"There were {count} complaints registered in the selected period."})

        if "were there" in user_input:
            count = get_complaint_stats(date_range)
            return jsonify({"response": "Yes" if count > 0 else "No"})

        if phone_number:
            history = get_repair_history(phone_number, year, status_filter, date_range)
            return jsonify({"response": history if history else "No complaint history found."})

        return jsonify({"response": "I can't understand that. Can you please ask something related to complaint history?"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
