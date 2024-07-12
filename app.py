import pandas as pd
from flask import Flask, request, render_template, session, redirect, url_for
import random
import os

app = Flask(__name__)
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
        correct_reading = words[words['漢字'] == kanji]['読み⽅'].values[0]
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
    session['kanji'] = row['漢字']
    session['attempts'] = 0
    return render_template("quiz_hiragana.html", kanji=row['漢字'], feedback="", done=False)

@app.route("/quiz_kanji", methods=["GET", "POST"])
def quiz_kanji():
    if 'seed' in session:
        random.seed(session['seed'])

    if request.method == "POST":
        kanji = session.get("kanji")
        user_input = request.form.get("user_input", "")
        correct_kanji = words[words['한국어'] == session.get("korean_word")]['漢字'].values[0]

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
    session['kanji'] = row['漢字']
    session['korean_word'] = row['한국어']
    session['attempts'] = 0
    return render_template("quiz_kanji.html", korean_word=row['한국어'], feedback="", done=False)

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
