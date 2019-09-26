import os
import secrets
from pathlib import Path
from PIL import Image
from flaskblog import app, db, bcrypt
from flask import render_template, url_for, redirect, flash, request, abort
from flaskblog.forms import RegistrationForm, LoginForm, AccountUpdateForm, PostForm
from flaskblog.models import User, Post
from flask_login import login_user, logout_user, login_required, current_user


# posts = [
#     {
#         "author": "Shubham Sharma",
#         "title": "Blog Post 1",
#         "content": "First Post Content",
#         "date_posted": "January 4, 2019",
#     },
#     {
#         "author": "Pulkit Sharma",
#         "title": "Blog Post 2",
#         "content": "Second Post Content",
#         "date_posted": "January 8, 2019",
#     },
# ]


@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.all()
    return render_template("home.html", posts=posts)


@app.route("/about")
def about():
    return render_template("about.html", title="About")


@app.route("/register", methods=["GET", "POST"])
def register():
    # If user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = RegistrationForm()  # New Registration form
    if form.validate_on_submit():  # If form data is valid

        hashed_pw = bcrypt.generate_password_hash(form.password.data).decode(
            "utf-8"
        )  # Encrypting User password

        user = User(
            username=form.username.data, email=form.email.data, password=hashed_pw
        )  # Creating new user object

        db.session.add(user)  # Adding user to database
        db.session.commit()  # Database commit

        flash(
            f"Your account has been created! You are now able to log in",
            category="success",
        )
        return redirect(url_for("login"))

    return render_template("register.html", title="Register", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    # If user is already logged in
    if current_user.is_authenticated:
        return redirect(url_for("home"))

    form = LoginForm()
    if form.validate_on_submit():
        # Fetching user from database
        user = User.query.filter_by(email=form.email.data).first()

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get("next")
            return redirect(next_page) if next_page else redirect(url_for("home"))

        else:
            flash(
                "Login Unsuccessful. Please check email and password", category="danger"
            )

    return render_template("login.html", title="Login", form=form)


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))


def save_picture(form_picture):
    random_hex = secrets.token_hex(8)  # Name
    ext = Path(form_picture.filename).suffix  # Extension
    picture_fn = random_hex + ext  # Picture filename
    picture_path = Path(app.root_path) / "static" / "profile_pics" / picture_fn

    # Modifying picture's size
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)

    i.save(str(picture_path))  # Saving modified picture

    return picture_fn  # Returning picture filename


@app.route("/account", methods=["GET", "POST"])
@login_required
def account():
    form = AccountUpdateForm()
    if form.validate_on_submit():
        if form.picture.data:  # If picture is provided
            old_picture_file = (
                Path(app.root_path)
                / "static"
                / "profile_pics"
                / current_user.image_file
            )
            if old_picture_file.exists():
                os.remove(old_picture_file)

            picture_file = save_picture(form.picture.data)
            current_user.image_file = picture_file

        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()

        flash("Your account has been updated successfully", category="success")
        return redirect(url_for("account"))

    elif request.method == "GET":
        form.username.data = current_user.username
        form.email.data = current_user.email

    image_file = url_for("static", filename="profile_pics/" + current_user.image_file)
    return render_template(
        "account.html", title="Account", image_file=image_file, form=form
    )


@app.route("/post/new", methods=["GET", "POST"])
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data, content=form.content.data, author=current_user
        )
        db.session.add(post)
        db.session.commit()

        flash("Your post has been created!", category="success")
        return redirect(url_for("home"))

    return render_template(
        "create_post.html", title="New Post", form=form, legend="New Post"
    )


@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)

    return render_template("post.html", title=post.title, post=post)


@app.route("/post/<int:post_id>/update", methods=["GET", "POST"])
def update_post(post_id):
    post = Post.query.get_or_404(post_id)

    if current_user != post.author:
        abort(403)

    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()

        flash("Your post have been updated!", category="success")
        return redirect(url_for("post", post_id=post.id))

    elif request.method == "GET":
        form.title.data = post.title
        form.content.data = post.content

    return render_template(
        "create_post.html", title="Update post", form=form, legend="Update Post"
    )


@app.route("/post/<int:post_id>/delete", methods=["POST"])
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)

    if current_user != post.author:
        abort(403)

    db.session.delete(post)
    db.session.commit()

    flash("Your post have been deleted!", category="success")
    return redirect(url_for("home"))

