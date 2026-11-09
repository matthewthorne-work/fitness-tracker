import sqlite3 # Import the SQLite3 library for database operations i.e. let's the Python code read and write to the local datebase file(fitness.db)
from datetime import date # Import the date class from the datetime module for handling dates
from flask import Flask, render_template, request, redirect, url_for # Flask is a web framework for building web applications. render_template is used to render HTML templates, request is used to handle incoming HTTP requests, redirect is used to redirect the user to a different URL, and url_for is used to generate URLs for specific routes in the application.

app = Flask(__name__) # Initialize the Flask application
DB_NAME = "fitness.db" # Assigning the datebase to a variable

def get_db(): 
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn # Connect and opens fitness.db if that file does not exist then it will create one. The row_factory attribute is set to sqlite3.Row, which allows us to access the columns of the result set by name. Then return will return the connection object, which can be used to execute SQL queries and interact with the database.

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTERGER PRIMANY KEY AUTOINCREMENT,
                workout_date TECT NOT NULL,
                slipt TEXT NOT NULL,
                exerice TEXT NOT NULL,
                weight REAL NOT NULL,
                sets INTEGER NOT NULL,
                reps INTGER NOT NULL,
                est_1rm REAL NOT NULL
            )
        """) # This function initializes the database by creating a table called workouts if it does not already exist. The table has columns for id, workout_date, split, exercise, weight, sets, reps, and est_1rm. The id column is an integer primary key that auto-increments with each new entry. The other columns store information about the workout.

def calculate_1rm(weight, reps):
    if reps == 1:
        return round(weight, 1)
    # Epley formula
    return round(weight * (1 + reps / 30), 1) # This function will calulate the 1 rep max. If you do 1 rep they the 1rm is what you lifted otherwise it will use Epley formula.

@app.route("/", methods = ["GET", "POST"])
def index():
    if request.method == "POST":
        workout_date = request.form["workout_date"]
        split = request.form["split"].strip()
        exercise = request.form["exercise"].strip().title
        weight = float(request.form["weight"])
        sets = int(request.form["sets"])
        reps = int(request.form["reps"])

        est_1rm = calculate_1rm(weight, reps)

        with get_db() as conn:
            conn.execute("""
                INSERT INTO workouts (workout_date, split, exercise, weight, sets, reps, est_1rm)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (workout_date, split, exercise, weight, sets, reps, est_1rm))

    return render_template("index.html") # This route handles both GET and POST requests to the root URL ("/"). If the request method is POST, it retrieves the workout data from the form submission, calculates the estimated 1-rep max using the calculate_1rm function, and inserts the data into the workouts table in the database. Finally, it renders the index.html template to display the form and any relevant information.

if __name__ == "__main__":
    init_db()
    app.run(debug=True) # This block checks if the script is being run directly (not imported as a module). If it is, it initializes the database by calling init_db() and starts the Flask development server with debug mode enabled. Debug mode provides detailed error messages and automatically reloads the server when code changes are detected.