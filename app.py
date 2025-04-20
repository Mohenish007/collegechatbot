"""from flask import Flask, render_template, request, session, redirect, url_for
from recommender import questions, extract_intent, calculate_relevancy

app = Flask(__name__)
app.secret_key = "your_secret_key_here"


@app.route("/", methods=["GET", "POST"])
def chat():
    if "answers" not in session:
        session["answers"] = {}
        session["current_q"] = 0

    if request.method == "POST":
        user_answer = request.form["answer"]
        key = questions[session["current_q"]][0]
        session["answers"][key] = extract_intent(key, user_answer)

        session["current_q"] += 1

        if session["current_q"] >= len(questions):
            return redirect(url_for("recommendations"))

    current_question = questions[session["current_q"]][1]
    return render_template("index.html", question=current_question)


@app.route("/recommendations")
def recommendations():
    user_input = session.pop("answers", {})
    session.pop("current_q", None)
    top_colleges = calculate_relevancy(user_input)
    return render_template("results.html", colleges=top_colleges.iterrows())


if __name__ == "__main__":
    app.run(debug=True)"""

from flask import Flask, render_template, request, jsonify, session
from recommender import questions, extract_intent, calculate_relevancy
import random

app = Flask(__name__)
app.secret_key = "secret123"  # Required for sessions

welcome_messages = [
    "Hi there! 👋 I'm your college recommendation assistant.",
    "Hello! Ready to discover the best colleges for you? 🎓",
    "Hey! Let's find your ideal college today. 😊",
]

@app.route("/")
def home():
    session.clear()  # reset answers if user reloads
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():
    user_message = request.json.get("message")

    if not user_message:
        return jsonify({"response": "Please type or say something!"})

    # Start chat — send greeting + first question
    if "question_index" not in session:
        session["question_index"] = 0
        session["answers"] = {}
        greeting = random.choice(welcome_messages)
        first_q = questions[0][1]
        return jsonify({"response": f"{greeting} {first_q}"})

    q_index = session["question_index"]
    answers = session["answers"]
    question_key = questions[q_index][0]

    # Extract and save answer
    answer = extract_intent(question_key, user_message)
    answers[question_key] = answer

    # Move to next question
    session["question_index"] = q_index + 1

    # If questions remain, ask next one
    if session["question_index"] < len(questions):
        next_q = questions[session["question_index"]][1]
        return jsonify({"response": next_q})

    # All questions answered: show results
    results = calculate_relevancy(answers)
    session.clear()

    if results.empty:
        return jsonify({"response": "Sorry, no colleges matched your preferences. 😢"})

    response_text = "🎓 Here are your top 5 recommended colleges:\n\n"
    for _, row in results.iterrows():
        response_text += (
            f"{row['college_name']} - {row['location']} ({row['course']})\n"
            f"Fee: ₹{row['fee']}, Exam: {row.get('relevant_exam', 'N/A')}, "
            f"Min Marks: {row.get('min_marks', 'N/A')}\n"
            f"Type: {row['type']}, Accreditation: {row['accreditation']}, "
            f"Scholarship: {'Yes' if row['scholarship'] else 'No'}\n\n"
        )

    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(debug=True)
