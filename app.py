from flask import Flask, render_template, redirect, request, session, flash, url_for
from flask_session import Session
from dotenv import load_dotenv
import os
import requests
import random

#load environment variable
load_dotenv()

#Setup flask
app = Flask(__name__)

#check and access secret key from dotenv
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise ValueError("No SECRET_KEY set in environment variables.")

app.config["SECRET_KEY"] = secret_key

# Set server-side storage to avoid cookie overload
app.config['SESSION_TYPE'] = 'filesystem' #files are stored in the filesystem
app.config['SESSION_PERMANENT'] = False #session restarts every time
app.config['SESSION_USE_SIGNER'] = True #cryptographically sign the session ID cookie
Session(app)

#Prevent caching of pages so that the user cannot go back and change answers (Chat GPT)
@app.after_request #applies headers to each response
def apply_headers(response):
    response.headers['Cache-Control'] = 'no-store, no-cache, must-revalidate' #browser doesn't store, needs to revalidate with server before using cached, and revalidates stale responses with server
    response.headers['Pragma'] = 'no-cache' #older header for backwards compatibility
    response.headers['Expires'] = '0' #response is already expired (0) so the browser needs to fetch a new one
    return response

#Main menu    
@app.route("/", methods= ["GET", "POST"])
def index():
    if request.method == "GET":
        
        #Generate token if there isn't one
        if "session_token" not in session:
            #error handling for API
            try:
                token_request = requests.get("https://opentdb.com/api_token.php?command=request", timeout=5)
                token_json = token_request.json()
                session["session_token"] = token_json["token"]

            except:
                flash("There was an error retrieving a token", "error")
                return render_template("index.html")

        #initialise player names
        if "p1_name" not in session:
            session["p1_name"] = "Player 1"
        if "p2_name" not in session:
            session["p2_name"] = "Player 2"

        #initialise num of questions
        if "questions_number" not in session:
            session["questions_number"] = 10

        return render_template("index.html")
            
    elif request.method == "POST":

        if request.form.get("menu") == "Play": #link to game mode
            return redirect(url_for("game_mode"))
        elif request.form.get("menu") == "Instructions": #link to instructions
            return redirect(url_for("instructions"))
        elif request.form.get("menu") == "Options": #link to options
            return redirect(url_for("options"))
        elif request.form.get("menu") == "Main menu": #link to come back from options/instructions
            return redirect(url_for("index"))

#Instructions page    
@app.route("/instructions")
def instructions():

    #Check for session token
    if "session_token" not in session:
        flash("Session not initialized. Please try again.", "error")
        return redirect(url_for("index"))

    return render_template("instructions.html")

#Options menu
@app.route("/options", methods=["GET", "POST"])
def options():
    if request.method == "GET":

        #Check for session token
        if "session_token" not in session:
            flash("Session not initialized. Please try again.", "error")
            return redirect(url_for("index"))
        
        return render_template("options.html", session=session)
    
    elif request.method == "POST":

        #Back to main menu 
        if request.form.get("button") == "Main menu":
            return redirect(url_for("index"))

        #Apply changes        
        else:
            #Get user input for names and update session
            session["p1_name"] = request.form.get("p1_name")
            session["p2_name"] = request.form.get("p2_name")

            #Get user input for number of questions and update session
            session["questions_number"] = int(request.form.get("questions_number"))

            #flash successful changes and redirect
            flash("Changes have been applied successfuly!", "success")
            return redirect(url_for("options"))

#Choose Single-Player or Multi-Player
@app.route("/game_mode", methods = ["GET", "POST"])
def game_mode():
    if request.method == "GET":

        #Check for session token
        if "session_token" not in session:
            flash("Session not initialized. Please try again.", "error")
            return redirect(url_for("index"))

        return render_template("game_mode.html")
    
    elif request.method == "POST":
        #initialise single player mode
        if request.form.get("game_mode") == "1 player": session["game_mode"] = "1 player"
        #initialise 2-player mode
        elif request.form.get("game_mode") == "2 players": session["game_mode"] = "2 players"

        return redirect(url_for("game_config"))
    

@app.route("/game_config", methods=["GET", "POST"])
def game_config():        
    if request.method == "GET":
        
        #Check for session token
        if "session_token" not in session:
                flash("Session not initialized. Please try again.", "error")
                return redirect(url_for("index"))
        
        # Redirect to index if the session is not initialized
        if "game_mode" not in session:
            flash("There was an unexpected error. Please try again.")
            return redirect(url_for("index"))
        
        #Get data from API
        #Get categories
        try:
            api_categories = requests.get("https://opentdb.com/api_category.php", timeout=5)
            data = api_categories.json()
        
        except:
            flash("There was an error fetching the categories. Please try again.", "error")
            return render_template("index.html")
        
        #initialise categories from api
        categories = data["trivia_categories"]

        #add categories to session for api use
        session["categories"] = categories

        #Add category names to list to be displayed on category screen
        category_names = []
        for i in categories:
            name = i["name"]
            category_names.append(name)
            
        return render_template("game_config.html", category_names=sorted(category_names))
            
    elif request.method == "POST":

        #Get difficulty and add to session
        session["chosen_difficulty"] = request.form.get("difficulty")

        #Get category and add to session
        session["chosen_category"] = request.form.get("category")

        return redirect(url_for("countdown"))
    
@app.route("/countdown", methods=["GET", "POST"])
def countdown():
    if request.method == "GET":
        
        #5 second countdown to avoid API overload

        #Check for session token
        if "session_token" not in session:
            flash("Session not initialized. Please try again.", "error")
            return redirect(url_for("index"))

        #initialise right / wrong answers session
        session["score"] = {}
        session["score"]["p1_correct"] = 0
        session["score"]["p1_incorrect"] = 0
        session["score"]["p2_correct"] = 0
        session["score"]["p2_incorrect"] = 0

        #initialise starting player
        session["active_player"] = 1

        return render_template("countdown.html")
    
    elif request.method == "POST":

        questions_number = str(session['questions_number']) #get number of questions from session
        chosen_difficulty = session['chosen_difficulty'] #get difficulty from session
        session_token = session['session_token'] #get token from session

        #Get questions from random categories
        if session["chosen_category"] == "Random":
            #Get questions from chosen difficulty
            if session["chosen_difficulty"] != "":
                try:
                    api_link = f"https://opentdb.com/api.php?amount={questions_number}&difficulty={chosen_difficulty}&token={session_token}"
                    questions_query = requests.get(api_link, timeout=5)
                except Exception as e:
                    flash(e, "error")
                    return redirect(url_for("index"))
                
            #Get questions of random difficulty
            else:
                try:
                    api_link = f"https://opentdb.com/api.php?amount={questions_number}&token={session_token}"
                    questions_query = requests.get(api_link, timeout=5)
                except Exception as e:
                    flash(e, "error")
                    return redirect(url_for("index"))
                
        #Get questions from selected category
        else:

            print(session["categories"])

            #Find category id by matching selected category name to category name from api
            for category in session["categories"]:
                if category["name"] == session["chosen_category"]:
                    category_id = str(category["id"])

            #Get questions of chosen difficulty
            if session["chosen_difficulty"] != "":
                try:
                    api_link = f"https://opentdb.com/api.php?amount={questions_number}&category={category_id}&difficulty={chosen_difficulty}&token={session_token}"
                    questions_query = requests.get(api_link, timeout=5)
                except Exception as e:
                    flash(e, "error")
                    return redirect(url_for("index"))
                
            #Get questions of random difficulty
            else:
                try:
                    api_link = f"https://opentdb.com/api.php?amount={questions_number}&category={category_id}&token={session_token}"
                    questions_query = requests.get(api_link, timeout=5)
                except Exception as e:
                    flash(e, "error")
                    return redirect(url_for("index"))
        
        #Turn API response into a json to access different data
        questions_response = questions_query.json()

        #Check for API response codes
        if questions_response["response_code"] == 1:
            flash("Could not return results. The API doesn't have enough questions for your query.", "error")
            return redirect(url_for("index"))
        
        elif questions_response["response_code"] == 2:
            flash("Arguments passed in aren't valid.", "error")
            return redirect(url_for("index"))

        elif questions_response["response_code"] == 3:            
            flash("Session not initialized. Please try again.", "error") 
            return redirect(url_for("index"))
        
        elif questions_response["response_code"] == 4:
            #Reset token
            try:
                api_link = f"https://opentdb.com/api_token.php?command=reset&token={session['session_token']}"
                token_request = requests.get(api_link, timeout=5)
                session["session_token"] = token_request.json()["token"]
            except Exception as e:
                flash(e, "error")
                return redirect(url_for("index"))

            flash("Session Token has returned all possible questions for the specified query. Token has been reset.", "error")
            return redirect(url_for("index"))
        
        elif questions_response["response_code"] == 5:
            flash("Too many requests have occurred. Each IP can only access the API once every 5 seconds.", "error")
            return redirect(url_for("index"))
        
        session["questions"] = questions_response['results']  #add questions to session  
        session["question_count"] = 0    #initialise question count

        return redirect(url_for("game_session"))


@app.route("/game_session", methods=["GET", "POST"])
def game_session():
    if request.method == "GET":

        #Check for session token
        if "session_token" not in session:
            flash("Session not initialized. Please try again.", "error")
            return redirect(url_for("index"))
    
        #Check if end of the game and return endscreen
        if session["question_count"] > session["questions_number"] - 1:
             if session["game_mode"] == "1 player":
                return render_template("p1_end_screen.html", session=session)
             else:
                return render_template("p2_end_screen.html", session=session)
             
        #If there are more questions, proceed
        else:

            #Get a question and render it on the game session tab
            question_data = session["questions"][session["question_count"]]

            #update question counter
            question_number = session["question_count"] + 1

            #Add options to game session
            options = []
            options.append(question_data["correct_answer"])
            for answer in question_data["incorrect_answers"]:
                options.append(answer)

            #randomize order of answers
            random.shuffle(options)

            # #Return game session with question and options
            return render_template("game_session.html", question_data=question_data, options=options,
                                                        question_number=question_number,
                                                        session=session)
    
    elif request.method == "POST":

        #Choices if endgame screen
        if request.form.get("next") == "Play again": #Choose a category and play again
            return redirect(url_for("game_config"))
        elif request.form.get("next") == "Main Menu": # Return to main menu
            return redirect(url_for("index"))

        #If not endgame, proceed with questions
        player_choice = request.form.get("option")  #Get player's answer

        #get correct answer and add to session
        session["current_correct_answer"] = session["questions"][session["question_count"]]["correct_answer"]
        
        #check if answer is correct and add to right / wrong answers
        #correct answer
        if player_choice == session["current_correct_answer"]:
            session["answer"] = "correct"
            if session["active_player"] == 1:
                session["score"]["p1_correct"] += 1
            else:
                session["score"]["p2_correct"] += 1
                
        #incorrect answer
        else:
            session["answer"] = "incorrect"
            if session["active_player"] == 1:
                session["score"]["p1_incorrect"] += 1
            else:
                session["score"]["p2_incorrect"] += 1

        #Change active player if 2 player mode
        if session["game_mode"] == "2 players":
            if session["active_player"] == 1:
                session["active_player"] = 2
            else:
                session["active_player"] = 1

        session["question_count"] += 1    #update question count

        return redirect(url_for("answer"))


@app.route("/answer", methods = ["GET", "POST"])
def answer():

    #Check for session token
    if "session_token" not in session:
        flash("Session not initialized. Please try again.", "error")
        return redirect(url_for("index"))

    #return single player score
    if session["game_mode"] == "1 player":
        return render_template("p1_answer.html", session = session)
    
    #return 2 player score
    else:
        return render_template("p2_answer.html", session = session)

if __name__ == '__main__':
    app.run(debug=os.getenv("FLASK_DEBUG", "False").lower() == "true")