import sqlite3 # Import the SQLite3 library for database operations i.e. let's the Python code read and write to the local datebase file(fitness.db)
from datetime import date # Import the date class from the datetime module for handling dates
from flask import Flask, render_template, request, redirect, url_for # Flask is a web framework for building web applications. render_template is used to render HTML templates, request is used to handle incoming HTTP requests, redirect is used to redirect the user to a different URL, and url_for is used to generate URLs for specific routes in the application.

app = Flask(__name__) # Initialize the Flask application
DB_NAME = "fitness.db" # Assigning the database to a variable

def get_db(): 
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn # Connect and opens fitness.db if that file does not exist then it will create one. The row_factory attribute is set to sqlite3.Row, which allows us to access the columns of the result set by name. Then return will return the connection object, which can be used to execute SQL queries and interact with the database.

def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS workouts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                workout_date TEXT NOT NULL,
                split TEXT NOT NULL,
                exercise TEXT NOT NULL,
                weight REAL NOT NULL,
                sets INTEGER NOT NULL,
                reps INTEGER NOT NULL,
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

        exercises = request.form.getlist("exercise[]")
        weights = request.form.getlist("weight[]")
        sets_list = request.form.getlist("sets[]")
        reps_list = request.form.getlist("reps[]")


        with get_db() as conn:

            for ex, w, s, r in zip(exercises, weights, sets_list, reps_list):
                if ex.strip():
                    exercise_name = ex.strip().title()
                    weight_val = float(w)
                    sets_val = int(s)
                    reps_val = int(r)
                    est_1rm = calculate_1rm(weight_val, reps_val)

            conn.execute("""
                INSERT INTO workouts (workout_date, split, exercise, weight, sets, reps, est_1rm)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (workout_date, split, exercise_name, weight_val, sets_val, reps_val, est_1rm)) # This block handles the submission of the workout log form. It retrieves the form data, including the workout date, split, exercises, weights, sets, and reps. It then calculates the estimated 1-rep max (est_1rm) for each exercise using the calculate_1rm function. Finally, it inserts the workout log into the workouts table in the database.

        return redirect(url_for("index")) # This will redirect the user back to the index page after submitting the workout log form.

    with get_db() as conn:
        logs = conn.execute("""
            SELECT * FROM workouts ORDER BY workout_date DESC, id DESC limit 20
            """).fetchall() # This block retrieves the last 20 workout logs from the workouts table in the database, ordered by workout_date in descending order and then by id in descending order. The results are stored in the logs variable.
        prs = conn.execute("""
            SELECT exercise, MAX(est_1rm) as best_1rm FROM workouts GROUP BY exercise ORDER BY exercise ASC
            """).fetchall() # This block retrieves the personal records (PRs) for each exercise from the workouts table in the database. It selects the exercise name and the maximum estimated 1-rep max (est_1rm) for each exercise, grouping the results by exercise and ordering them alphabetically. The results are stored in the prs variable.
        
    return render_template("index.html", logs=logs, prs=prs, today=date.today().isoformat) # The retrieved logs are passed to the index.html template for rendering. The template will display the workout logs on the web page.


if __name__ == "__main__":
    init_db()
    app.run(debug=True) # This block checks if the script is being run directly (not imported as a module). If it is, it initializes the database by calling init_db() and starts the Flask development server with debug mode enabled. Debug mode provides detailed error messages and automatically reloads the server when code changes are detected.