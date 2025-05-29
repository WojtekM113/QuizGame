import html, time, random, requests
from flask import Flask, redirect, render_template, request, session,  url_for, flash, get_flashed_messages

class Player:
    def __init__(self, name):
        self.name = name
        self.points = 0
        self.questions = []
        
    def add_point(self):
        self.points += 1

    def reset_points(self):
        self.points = 0
        
    def set_questions(self, questions):
        self.questions = questions
    
app = Flask(__name__)
MAX_PLAYERS = 4
 

all_players = []
app.secret_key = "your_secret_key_here"

@app.route("/", methods=["GET", "POST"])
def index():
    global all_players
 
    if request.method == "POST":
        
        number = request.form.get("numberOfQuestions")
        if number:
            session["number_of_questions"] = int(number)
            return redirect(url_for("index"))

        player_name = request.form.get("player")
        if player_name and all(player.name != player_name for player in all_players):
            all_players.append(Player(player_name))
        else:
            flash("Player with that name already exists")
        return render_template("index.html", players_names=all_players, number_of_questions=session.get("number_of_questions"))
    return render_template("index.html", players_names=all_players, number_of_questions= session.get("number_of_questions"))


@app.route("/clear")
def clear():
    global all_players
    all_players.clear()
    return redirect(url_for("index"))

@app.route("/game", methods=["GET", "POST"])
def gameView():
    global all_players
    if not all_players:
        flash("There is no players")
        return redirect(url_for("index"))       
  
    if all(not player.questions for player in all_players):
        return render_template("index.html", players=all_players)
    
    if 'current_player_index' not in session:
        session['current_player_index'] = 0

    active_players = [players for players in all_players if players.questions]

    current_index = session['current_player_index'] % len(active_players)
    current_player = active_players[current_index] 

    current_question = current_player.questions[0]
    question = current_question["question"]
    correct_answer = current_question["correct_answer"]
    wrong_answer = current_question["incorrect_answers"]

    all_answers = [correct_answer] + wrong_answer
    labeled_answers = {label: ans for label, ans in zip(["A", "B", "C", "D"], all_answers)}

    if request.method == "POST":
        selected = request.form.get("answer")
        if selected ==  correct_answer:
            current_player.add_point()
        

        current_player.questions.pop(0)

        session['current_player_index'] = (current_index + 1) % len(active_players)
        redirect(url_for("gameView"))
    return render_template("gameView.html", Question=question, answers=labeled_answers)

 
@app.route("/loadingScreen", methods=['GET', 'POST'])
def loading():
    global all_players
    
    if not all_players:
        flash("No players added!")
        return redirect(url_for("index"))
    
    number = session.get("number_of_questions", 1)
    total_questions = number * len(all_players) - 1
    
    response = requests.get(f"https://opentdb.com/api.php?amount={total_questions}&type=multiple")
    data = response.json()
    
    if "results" not in data or len(data["results"]) < total_questions:
        flash("Not enough questions available try again later.")
        return redirect(url_for("index"))
    
    questions = data["results"]
    
    # Assign questions evenly and reset points
    for i, player in enumerate(all_players):
        start = i * number
        end = start + number
        player.set_questions(questions[start:end])
        player.reset_points()
    
    # Initialize game state
    session['current_player_index'] = 0
    
    # Redirect to game
    return redirect(url_for("gameView"))
# @app.route("/answered")

 
             