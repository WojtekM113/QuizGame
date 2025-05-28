import html, time, random, requests
from flask import Flask, redirect, render_template, request,  url_for, flash, get_flashed_messages

class Player:
    def __init__(self, name):
        self.name = name
        self.points = 0

    def add_point(self):
        self.points += 1

    def reset_points(self):
        self.points = 0

app = Flask(__name__)
MAX_PLAYERS = 4

all_players = []
app.secret_key = "your_secret_key_here"

@app.route("/", methods=["GET", "POST"])
def index():
    global all_players
    if request.method == "POST":
        player_name = request.form.get("player")
        if player_name and all(player.name != player_name for player in all_players):
           if len(all_players) >= MAX_PLAYERS:
               flash("You cant add more players")
           else:   
            all_players.append(Player(player_name)) 
        return render_template("index.html", players_names=all_players)
    all_players.clear()
    return render_template("index.html", players_names=all_players)

@app.route("/clear")
def clear():
    global all_players
    all_players.clear
    return redirect(url_for("index"))

@app.route("/game", methods=["GET", "POST"])
def gameView():
    global all_players
    if not all_players:
        flash("There is no players")
        return redirect(url_for("index"))       
    
    max_retries = 5
    for attempt in range(max_retries):
        response = requests.get("https://opentdb.com/api.php?amount=1&type=multiple")
        try:
            data = response.json()  
            if "results" in data and data["results"]:
                break  
        except Exception:
            pass
        time.sleep(1)  # wait a second before retrying
    else:
        # This else corresponds to the for-loop: runs if no break
        flash("Failed to load quiz question after several tries. Please try again later.")
        return redirect(url_for("index"))

    result = data["results"][0]

    question = html.unescape(result['question'])
    correct_answer = html.unescape(result['correct_answer'])
    incorrect_answer = [html.unescape(ans) for ans in result['incorrect_answers']]

    all_answers = incorrect_answer + [correct_answer]
    random.shuffle(all_answers)
    
    labeled_answers = dict(zip(["A", "B", "C", "D"], all_answers))

    correct_label = [label for label, answer in labeled_answers.items() if answer == correct_answer][0]

    if request.method == "POST":
        selected = request.form.get("answer")
        if selected ==  correct_label:
            return redirect(url_for("gameView"))  
    return render_template("gameView.html", Question=question, answers=labeled_answers)

 
# @app.route("/answered")
