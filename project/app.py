import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Configure session to use filesystem (instead of signed cookies)
# Do to the nature of this project being short term and seldom used at the moment I'm sticking with filesystem
##IMPORTANT## If I choose to expand on this project for wider use, I'll change over to signed cookies for added security
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure Library to use SQLite database
##IMPORTANT## Change the name below to the actual database's name once I've decided on a name for the project
db = SQL("sqlite:///deliveright.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/", methods=["GET", "POST"])
@login_required
def contacts():
    """Show main page"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Get the user ID based on which column button is clicked in contacts page
        user_id = request.form.get('user_id')

        # Remove other user's Contact data from current user's contact list
        db.execute("DELETE FROM contactlist? WHERE user_id = ?", session["user_id"], user_id)
        # Redirect user to contacts page
        return redirect("/")

    # User reached route via GET (as by clicking a link)
    elif request.method == "GET":

        contacts = db.execute("SELECT * FROM contactlist?", session["user_id"])
        profile = db.execute("SELECT * FROM users WHERE id=:user", user=session["user_id"])
        type = str(profile[0]["type"])

        if contacts == None:
            return render_template("contacts.html")

        else:
            if type == "owner":
                addtype = "City"
                return render_template("contacts.html", contacts=contacts, addtype=addtype)

            elif type == "driver":
                addtype = "Address"
                return render_template("contacts.html", contacts=contacts, addtype=addtype)


@app.route("/search", methods=["GET", "POST"])
@login_required
def search():
    """Search other Users' profiles"""

    # User reached route via GET
    if request.method == "GET":

        profile = db.execute("SELECT * FROM users WHERE id=:user", user=session["user_id"])
        type = str(profile[0]["type"])
        city = str(profile[0]["city"])

        # Pass in certain variables for fields if the user is an owner looking for drivers
        if type == "owner":
            name = ((db.execute("SELECT firstname FROM users WHERE city = ?", city)) + (db.execute("SELECT lastname FROM users WHERE city = ?", city)))
            addtype = ("City")
            email = db.execute("SELECT email FROM users WHERE city = ?", city)
            address = db.execute("SELECT city FROM users WHERE city = ?", city)

            # Pass in other users' into search.html
            return render_template("search.html", addtype=addtype, name=name, address=address, email=email)

        # Pass in certain variables for fields if the user is an driver looking for owners
        elif type == "driver":
            name = db.execute("SELECT restname FROM users WHERE city = ?", city)
            addtype = ("Address")
            email = db.execute("SELECT email FROM users WHERE city = ?", city)
            address = ((db.execute("SELECT street FROM users WHERE city = ?", city)) + (db.execute("SELECT city FROM users WHERE city = ?", city)) + (db.execute("SELECT state FROM users WHERE city = ?", city)) + (db.execute("SELECT zip FROM users WHERE city = ?", city)))

            # Pass in other users' into search.html
            return render_template("search.html", addtype=addtype, name=name, address=address, email=email)

    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":
        # Grab info for contact list from search page
        name = request.form.get("name")
        email = request.form.get("email")
        address = request.form.get("address")
        # Function to add selected user to current user's contact list
        db.execute("INSERT INTO contactlist? (name, email, address) VALUES (?, ?, ?)", session["user_id"], name, email, address)
        return redirect("/")


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Display User's profile"""

    # User reached route via GET
    if request.method == "GET":

        # Get current historical data to pass into variable for html file
        profile = db.execute("SELECT * FROM users WHERE id=:user", user=session["user_id"])
        usertype = str(profile[0]["type"])

        # IF AND ELIF BASED ON USER TYPE TO DIRECT USER TO DIFFERENT SITE BASED ON TYPE
        # Pass in profile Table into profile.html
        if usertype == "owner":
            return render_template("profile1.html", profile=profile)

        elif usertype == "driver":
            return render_template("profile2.html", profile=profile)

    # FOR UPDATE PAGE
    # User reached route via POST (as by submitting a form via POST)
    elif request.method == "POST":

        profile = db.execute("SELECT * FROM users WHERE id=:user", user=session["user_id"])
        usertype = str(profile[0]["type"])

        if usertype == "owner":
            return redirect("/update_owner")

        elif usertype == "driver":
            return redirect("/update_driver")


@app.route("/update_owner", methods=["GET", "POST"])
@login_required
def update_owner():
    """Display User's profile"""

    # User reached out via POST (as by clicking a link or via redirect)
    if request.method == "POST":
        # UPDATE user info into users table if fields are filled out
        # Pull in current data, in case there are NULL fields
        current_restname = db.execute("SELECT restname FROM users WHERE id=:user", user=session["user_id"])
        current_firstname = db.execute("SELECT firstname FROM users WHERE id=:user", user=session["user_id"])
        current_lastname = db.execute("SELECT lastname FROM users WHERE id=:user", user=session["user_id"])
        current_username = db.execute("SELECT username FROM users WHERE id=:user", user=session["user_id"])
        current_email = db.execute("SELECT email FROM users WHERE id=:user", user=session["user_id"])
        current_street = db.execute("SELECT street FROM users WHERE id=:user", user=session["user_id"])
        current_city = db.execute("SELECT city FROM users WHERE id=:user", user=session["user_id"])
        current_state = db.execute("SELECT state FROM users WHERE id=:user", user=session["user_id"])
        current_zip = db.execute("SELECT zip FROM users WHERE id=:user", user=session["user_id"])

        # Update existing data if rows not NULL
        db.execute("UPDATE users SET restname = coalesce(?, ?), firstname = coalesce(?, ?), lastname = coalesce(?, ?), username = coalesce(?, ?), email = coalesce(?, ?), street = coalesce(?, ?), city = coalesce(?, ?), state = coalesce(?, ?), zip = coalesce(?, ?) WHERE id = ?",
            request.form.get("restname"), current_restname,
            request.form.get("firstname"), current_firstname,
            request.form.get("lastname"), current_lastname,
            request.form.get("username"), current_username,
            request.form.get("email"), current_email,
            request.form.get("street"), current_street,
            request.form.get("city"), current_city,
            request.form.get("state"), current_state,
            request.form.get("zip"), current_zip,
            session["user_id"])


        # Redirect user to profile page
        return redirect("/profile")


    # User reached route via GET
    elif request.method == "GET":
        profile = db.execute("SELECT * FROM users WHERE id=:user", user=session["user_id"])
        return render_template("update_owner.html", profile=profile)



@app.route("/update_driver", methods=["GET", "POST"])
@login_required
def update_driver():
    """Display User's profile"""

    # User reached out via POST (as by clicking a link or via redirect)
    if request.method == "POST":
        # UPDATE user info into users table if fields are filled out
        # Pull in current data, in case there are NULL fields
        current_firstname = db.execute("SELECT firstname FROM users WHERE id=:user", user=session["user_id"])
        current_lastname = db.execute("SELECT lastname FROM users WHERE id=:user", user=session["user_id"])
        current_username = db.execute("SELECT username FROM users WHERE id=:user", user=session["user_id"])
        current_email = db.execute("SELECT email FROM users WHERE id=:user", user=session["user_id"])
        current_city = db.execute("SELECT city FROM users WHERE id=:user", user=session["user_id"])

        # Update existing data if rows not NULL
        db.execute("UPDATE users SET firstname = coalesce(?, ?), lastname = coalesce(?, ?), username = coalesce(?, ?), email = coalesce(?, ?), city = coalesce(?, ?) WHERE id = ?",
            request.form.get("firstname"), current_firstname,
            request.form.get("lastname"), current_lastname,
            request.form.get("username"), current_username,
            request.form.get("email"), current_email,
            request.form.get("city"), current_city,
            session["user_id"])


        # Redirect user to profile page
        return redirect("/profile")


    # User reached route via GET
    elif request.method == "GET":
        profile = db.execute("SELECT * FROM users WHERE id=:user", user=session["user_id"])
        return render_template("update_driver.html", profile=profile)



@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)
        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/delete", methods=["GET", "POST"])
def delete():
    """Delete User's profile"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Delete user data from users and contact list
        db.execute("DROP TABLE [IF EXISTS] contactlist?", session["user_id"])
        db.execute("DELETE FROM users WHERE id=:user", user=session["user_id"])[0]
        # Forget any user_id
        session.clear()

        # Redirect user to login form
        return redirect("/")

    # User reached route via GET (as by clicking a link)
    elif request.method == "GET":
         return render_template("delete.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Grab Password and Confirmation for later use
        reg_password=request.form.get("password")
        reg_confirmation=request.form.get("confirmation")

        # Grab type for later use
        reg_type=request.form.get("type")

        # Ensure firstname was submitted
        if not request.form.get("firstname"):
            return apology("missing first name", 400)

        # Ensure lastname was submitted
        if not request.form.get("lastname"):
            return apology("missing last name", 400)

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("missing username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("missing password", 400)

        # Ensure password confirmation was submitted
        elif not request.form.get("confirmation"):
            return apology("passwords don't match", 400)

        # Ensure passwords match
        elif not reg_password==reg_confirmation:
            return apology("passwords don't match", 400)

        # Ensure type is selected
        elif not reg_type:
            return apology("missing type", 400)

        # Both user types need to fill out city info
        elif not request.form.get("city"):
            return apology("missing city name", 400)

        #Both user types need to fill out email info
        elif not request.form.get("email"):
            return apology("missing email address", 400)

        # Information Owners only need to fill out
        if reg_type=="owner":

            if not request.form.get("restname"):
                return apology("missing restaurant name", 400)

            elif not request.form.get("street"):
                return apology("missing street address", 400)

            elif not request.form.get("state"):
                return apology("missing state name", 400)

            elif not request.form.get("zip"):
                return apology("missing zip code", 400)

        # Ensure username doesn't already exist
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        if len(rows) >= 1:
            return apology("Username is not available", 400)

        # Insert user info into users table on registry in database
        db.execute("INSERT INTO users (firstname, lastname, username, email, hash, type, restname, street, city, state, zip) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", request.form.get("firstname"), request.form.get("lastname"), request.form.get("username"), request.form.get("email"), generate_password_hash(request.form.get("password"), method='pbkdf2:sha256', salt_length=8), reg_type, request.form.get("restname"), request.form.get("street"), request.form.get("city"), request.form.get("state"), request.form.get("zip"))

        # Automatically log user in
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))
        session["user_id"] = rows[0]["id"]

        # Create Client list for each user on sign up
        db.execute("CREATE TABLE contactlist (user_id INTEGER NOT NULL, user_type TEXT NOT NULL, name TEXT NOT NULL, email TEXT NOT NULL, address TEXT NOT NULL, FOREIGN KEY(user_id) REFERENCES users(id))")
        db.execute("ALTER TABLE contactlist RENAME TO contactlist?", session["user_id"])

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")

