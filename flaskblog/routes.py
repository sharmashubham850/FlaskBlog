from flaskblog import app
from flask import render_template, url_for, redirect, flash
from flaskblog.forms import RegistrationForm, LoginForm
from flaskblog.models import User, Post


posts = [
    {
        "author": "Shubham Sharma",
        "title": "Blog Post 1",
        "content": "First Post Content",
        "date_posted": "January 4, 2019",
    },
    {
        "author": "Pulkit Sharma",
        "title": "Blog Post 2",
        "content": "Second Post Content",
        "date_posted": "January 8, 2019",
    },
]


@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        flash(f"Account created for {form.username.data}!", category="success")
        return redirect(url_for("home"))

    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if form.email.data == "admin@blog.com" and form.password.data == "sharma850":
            flash("You have been logged in", category="success")
            return redirect(url_for("home"))

        else:
            flash(
                "Invalid credentials. Check your email or password", category="danger"
            )

    return render_template("login.html", title="Login", form=form)
