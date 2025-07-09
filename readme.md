# TriviaFight
## Video Demo:  [https://youtu.be/9_tWAWa9wmE](https://youtu.be/9_tWAWa9wmE)
## Description:

TriviaFight is a fun web-based quiz game for 1 to 2 players. It uses questions from the [Open Trivia Database](https://opentdb.com/) API and players can choose from a wide range of categories as well as the difficulty of the questions. 

There is a "single player" mode where a player answers a set number of questions trying to get more correct than incorrect answers and also a "multiplayer" mode where players take turns on the same device trying to score more correct answers than the other player. The questions follow a "multiple choice" and "true/false" format.

As an extra feature, the players can change their names and the number of questions can be set from 8 to 20 questions per round at the "Options" menu.

The back-end of TriviaFight is written in Python utilising the Flask framework. The API requests are handled with the "Requests" library and the API data (questions, answers) as well as other information is stored locally on the filesystem through "flask sessions". The combination of Python and Flask provides a seamless way to organise the logic of the different pages of the application as well as to present the pages on the user's browser. At the same time information relevant to the game is stored on the "session" cookie which provides easy and quick local access. 

> [!NOTE]
> Since this is a personal project focusing on the use of Python/Flask along with the front-end elements, data is stored locally for convenience. In its "production" form, this project would utilise a temporary SQL database for data storage, however database integration falls outside the scope of the endeavour. It remains a feature to be added as an update.

The app has also been deployed on [Render](https://render.com/) with the use of [gunicorn](https://gunicorn.org/). TriviaFight on Render can be accessed with [this link](https://triviafight.onrender.com/)

The front-end of TriviaFight utilises HTML (in conjunction with [Jinja2](https://jinja.palletsprojects.com/en/stable/)) and CSS. Moreover, the [Bootstrap 5](https://getbootstrap.com/) framework is used to provide a clean and minimalist look to the pages while keeping the code neatly organised. The website works on PC, tablets and smartphones through responsive design and media queries. There are also 2 Javascript functions within the code: 1. A slider on the options menu and 2. a countdown function that triggers an API call and starts the game.

Since this was my first full-stack project, satisfactory implementation of front-end best practices, responsiveness and the mobile-first approach was my main challenge and I am sure there are a lot of improvements that can be made. Upon review of the code, changes will be made regarding the responsive design of the buttons and their re-sizing on extra large screens. 

As mentioned before, a SQL database is another feature that can be used to replace local storage through "flask sessions".

Finally, should an appropriate API be found, AI integration is a feature that could substantially add to this project through AI-generated questions based on users' prompts.

## Files description
 
### app.py
 This is the main back-end logic behind TriviaFight. It is a Python app that utilizes the Flask framework to organize the different HTML pages of the app (listed below). As mentioned before, important information (such as player names, number of questions etc) along with API data (questions and options) are stored in flask "Sessions" which are set up to use local storage in the filesystem. As a flask app, the application also needs a secret key which can be found in the ".env" file and the values are passed into the app with the use of the "dotenv" library. Finally, the API calls are handled through the "Requests" library.

### layout.html
 This is the HTML template on which the rest of the pages are built. It utilizes Jinja syntax so that the rest of the pages can be rendered when called upon. It utilizes responsive design and it introduces the Bootstrap 5 framework.

### index.html
 This is the main menu page of TriviaFight. It includes the Play, Instructions and Options buttons. Also, the error messages from other pages of the app are displayed here at the bottom of the page through flask alerts. At any point (as with the other pages as well) the user can click on the TriviaFight logo to return to the main screen.

### instructions.html
 In the Instructions page the user can read some general information on how to play the game.

### options.html
 In this page the player can change the names that are displayed during the game session. Also they can change the number of questions that each round includes. This is one of the 2 Javascript functions that are used in TriviaFight and its purpose is to control the slider for choosing the number of questions.  

### game_mode.html
 This is where the player chooses single or 2-player mode.

### game_config.html
 In this page, the player can choose the difficulty of the questions or choose to get questions of different difficulties. Similarly, the player can choose a specific category or click on "Random" to get questions from different categories. 

### countdown.html
 This page serves as an intermediary between the config and the game session pages. It includes the second Javascript function of this application in the form a countdown timer, which triggers the start of the game. 

### game_session.html
 This is the main page of the game where the player can interact with data from the API. At the top of the page the player can see information about who the active player is, the category and the difficulty of the question. On the main window the question is displayed along with buttons that contain the answer options (4 for multiple choice and 2 for true/false). At the bottom of the page the player can also see how many questions are left. This page uses iteration on the API question data to display the answer options. In the case of a True/False question, iteration was avoided so that the buttons always show "True" first and "False" second.

### answer.html
 This is where the results of each answer are displayed. The HTML page uses a conditional statement to check whether the answer was correct or not, utilizing session data. Also the player can see their score up to that point (correct/incorrect answers). 

### endscreen.html
 This is the final page of a game round. It displays the final result of the game again utilizing a conditional statement that checks the number of correct answers to incorrect ones. As in the "answer" page, the player can also see the final score. The player has the choice of starting another round (which redirects them to the config screen) or to go back to the main menu.

### style.css
 This is the css file that contains front-end customizations that could not be done with the use Bootstrap. It utilises a global font from [Google APIs](https://developers.google.com/apis-explorer) and a limited amount of media queries, since most of the responsive design is handled by bootstrap. Most of the buttons keep their original size in smaller and larger screens but change direction from row to collumn. Most of the fonts utilise clamp to change size dynamically based on screen size. 

### requirements.txt
 This is the file that includes all the necessary dependencies that are needed to setup the application.

### .env.example
This file serves as an example for the actual .env file that needs to be included by the user in order to successfully run the app. It contains only two lines. The first one is the flask secret key that the user needs to generate. The second one is optional and it toogles debug mode for flask.

### .gitignore
This file includes the things that should be ignored when updating the repository on GitHub. It is mainly there so that future updates can be made without changing environment variables or adding unecessary files (like "flask_sessions") to the repository.

### secret_key_generator.py

The user should run this python script to get a new secret key that can be copied and pasted on the .env file so that Flask can function properly.
 
## How to install and run

### Clone repository

On cmd:

    git clone https://github.com/ManosKelig/TriviaFight-Web-Based-Quiz-Game

then:

    cd TriviaFight-Web-Based-Quiz-Game

or download from GitHub

###  Setup virtual environment 
To run this application it is recommended that the user setup and activate a virtual environment so that the dependencies of the application can be installed without conflicting with other versions.

#### Create the environment

    python -m venv venv

#### Activate environment

    venv\Scripts\activate

### Set a secret key

Change the name of '.env.example' to '.env' copy the output of 'secret_key_generator.py'.

### Install dependencies and run
After the virtual environment and the key have been set up, it necessary to install the dependencies that are needed for the app to run. The requirements.txt file can be used to install them through the terminal. To do this, execute the following line in the virtual environment terminal 

    pip install -r requirements.txt. 

After the dependencies have been installed, run "app.py" from the terminal.


## How to use the project

Using TriviaFight is straightforward. After completing the setup and running "app.py" from the terminal, the user should go to [http://127.0.0.1:5000](http://127.0.0.1:5000) on their browser.

From there, the user can easily navigate through the different pages by using the bootstrap buttons and the other interactive elements that TriviaFight contains.

## License

## License

This project is not licensed for reuse. It is publicly available for demonstration and portfolio purposes only.