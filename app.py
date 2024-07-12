import pandas as pd
from flask import Flask, request, render_template, session, redirect, url_for
import random
import os

app = Flask(__name__, static_folder='static')
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'fallback_secret_key')

# Load the data into 'words'
data_path = "kanji_data.xlsx"
words = pd.read_excel(data_path)

@app.route("/", methods=["GET"])
def home():
    return render_template("index.html")

@app.route("/quiz_hiragana", methods=["GET", "POST"])
def quiz_hiragana():
    if 'seed' in session:
        random.seed(session['seed'])

    if request.method == "POST":
        user_input = request.form.get("reading")
        kanji = session.get("kanji")
        correct_reading = words[words['kanji_word'] == kanji]['yomikata_word'].values[0]
        if user_input == correct_reading:
            feedback = "Correct!"
            return render_template("quiz_hiragana.html", feedback=feedback, done=True)
        else:
            session['attempts'] = session.get('attempts', 0) + 1
            if session['attempts'] >= 3:
                feedback = f"Incorrect! The correct reading is: {correct_reading}"
                session.pop('attempts', None)
                return render_template("quiz_hiragana.html", feedback=feedback, done=True)
            else:
                feedback = "Incorrect! Try again."
                return render_template("quiz_hiragana.html", kanji=kanji, feedback=feedback, done=False)

    row = words.sample().iloc[0]
    session['kanji'] = row['kanji_word']
    session['attempts'] = 0
    return render_template("quiz_hiragana.html", kanji=row['kanji_word'], feedback="", done=False)

@app.route("/quiz_kanji", methods=["GET", "POST"])
def quiz_kanji():
    if 'seed' in session:
        random.seed(session['seed'])

    if request.method == "POST":
        kanji = session.get("kanji")
        user_input = request.form.get("user_input", "")
        correct_kanji = words[words['hangul_word'] == session.get("korean_word")]['kanji_word'].values[0]

        if user_input == correct_kanji:
            feedback = "Correct!"
            done = True
        else:
            session['attempts'] = session.get('attempts', 0) + 1
            if session['attempts'] >= 3:
                feedback = f"Incorrect! The correct Kanji is: {correct_kanji}"
                done = True
            else:
                feedback = "Incorrect! Try again."
                done = False

        if done:
            session.pop('attempts', None)

        return render_template("quiz_kanji.html", feedback=feedback, done=done, korean_word=session.get("korean_word"))

    row = words.sample().iloc[0]
    session['kanji'] = row['kanji_word']
    session['korean_word'] = row['hangul_word']
    session['attempts'] = 0
    return render_template("quiz_kanji.html", korean_word=row['hangul_word'], feedback="", done=False)

@app.route("/weekly_kanji_quiz", methods=["GET", "POST"])
def weekly_kanji_quiz():
    if request.method == "POST":
        try:
            num_rows = int(request.form['num_rows'])
            session['selected_rows'] = words.sample(n=num_rows).to_dict(orient='records')
            return redirect(url_for('display_weekly_kanji_quiz'))
        except ValueError:
            return render_template("weekly_kanji_quiz.html", error="Please enter a valid number")
    return render_template("weekly_kanji_quiz.html")

@app.route("/display_weekly_kanji_quiz", methods=["GET"])
def display_weekly_kanji_quiz():
    selected_rows = session.get('selected_rows', [])
    print("Selected rows:", selected_rows)  # Debug: print the data
    return render_template("display_weekly_kanji_quiz.html", rows=selected_rows)

@app.route("/answers_weekly_kanji_quiz", methods=["GET"])
def answers_weekly_kanji_quiz():
    selected_rows = session.get('selected_rows', [])
    return render_template("answers_weekly_kanji_quiz.html", rows=selected_rows)

@app.route("/set_seed", methods=["POST"])
def set_seed():
    seed = request.form.get("seed")
    if seed:
        try:
            seed = int(seed)
            random.seed(seed)
            session['seed'] = seed
        except ValueError:
            return "Invalid seed. Please enter a valid integer.", 400
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
