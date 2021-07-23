import os

from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, LoginForm, MessageForm, UpdateUserForm, CsrfOnlyForm
from models import db, connect_db, User, Message

CURR_USER_KEY = "curr_user"
DEFAULT_IMG = "/static/images/default-pic.png"
DEFAULT_HEADER_IMG = "/static/images/warbler-hero.jpg"


app = Flask(__name__)

# Get DB_URI from environ variable (useful for production/testing) or,
# if not set there, use development local db.
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('DATABASE_URL', 'postgresql:///warbler'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
toolbar = DebugToolbarExtension(app)

connect_db(app)


##############################################################################
# User signup/login/logout

@app.before_request
def create_csrf_only_form():
    g.csrf_form = CsrfOnlyForm()


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER_KEY in session:
        g.user = User.query.get(session[CURR_USER_KEY])

    else:
        g.user = None


def do_login(user):
    """Log in user."""

    session[CURR_USER_KEY] = user.id


def do_logout():
    """Logout user."""

    if CURR_USER_KEY in session:
        del session[CURR_USER_KEY]


@app.route('/signup', methods=["GET", "POST"])
def signup():
    """Handle user signup.

    Create new user and add to DB. Redirect to home page.

    If form not valid, present form.

    If the there already is a user with that username: flash message
    and re-present form.
    """

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                image_url=form.image_url.data or User.image_url.default.arg,
            )
            db.session.commit()

        except IntegrityError:
            flash("Username or Email already taken", 'danger')
            return render_template('users/signup.html', form=form)

        do_login(user)

        return redirect("/")

    else:
        return render_template('users/signup.html', form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    """Handle user login."""

    form = LoginForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data,
                                 form.password.data)

        if user:
            do_login(user)
            flash(f"Hello, {user.username}!", "success")
            return redirect("/")

        flash("Invalid credentials.", 'danger')

    return render_template('users/login.html', form=form)


@app.route('/logout', methods=['POST'])
def logout():
    """Handle logout of user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if g.csrf_form.validate_on_submit():
        do_logout()
        flash('User successfully logged out', "success")
        return redirect('/login')

    flash('No logged in user', "danger")
    return redirect('/login')

    


##############################################################################
# General user routes:

@app.route('/users')
def list_users():
    """Page with listing of users.

    Can take a 'q' param in querystring to search by that username.
    """

    search = request.args.get('q')

    if not search:
        users = User.query.all()
    else:
        users = User.query.filter(User.username.like(f"%{search}%")).all()

    return render_template('users/index.html', users=users)


@app.route('/users/<int:user_id>')
def users_show(user_id):
    """Show user profile."""

    user = User.query.get_or_404(user_id)

    return render_template('users/show.html', user=user)


@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    """Show list of people this user is following."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/following.html', user=user)


@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    """Show list of followers of this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/followers.html', user=user)


@app.route('/users/<int:user_id>/likes')
def users_likes(user_id):
    """Show list of user's likes"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    user = User.query.get_or_404(user_id)
    return render_template('users/likes.html', user=user)


@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    """Add a follow for the currently-logged-in user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if g.csrf_form.validate_on_submit():
        followed_user = User.query.get_or_404(follow_id)
        g.user.following.append(followed_user)
        db.session.commit()

        return redirect(f"/users/{g.user.id}/following")

    flash('Unauthorized form submitted', "danger")
    return redirect('/logout')

@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    """Have currently-logged-in-user stop following this user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if g.csrf_form.validate_on_submit():
        followed_user = User.query.get(follow_id)
        g.user.following.remove(followed_user)
        db.session.commit()

        return redirect(f"/users/{g.user.id}/following")

    flash('Unauthorized form submitted', "danger")
    return redirect('/logout')


@app.route('/users/profile', methods=["GET", "POST"])
def update_profile():
    """Update profile for current user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")


    user = User.query.get_or_404(g.user.id)
    form = UpdateUserForm(obj=user)

    if form.validate_on_submit():
        if not User.authenticate(username=user.username, password=form.password.data):
            new_form = UpdateUserForm(obj={
                                "username": form.username.data,
                                "email": form.email.data,
                                "image_url": form.image_url.data or DEFAULT_IMG,
                                "header_image_url": form.header_image_url.data or DEFAULT_HEADER_IMG,
                                "location": form.location.data,
                                "bio": form.bio.data
                                })
            flash("Incorrect Password", "danger")
            return render_template("users/edit.html",
                                    form=new_form)

        user.username = form.username.data
        user.email = form.email.data
        user.image_url = form.image_url.data or DEFAULT_IMG
        user.header_image_url = form.header_image_url.data or DEFAULT_HEADER_IMG
        user.bio = form.bio.data
        user.location = form.location.data

        db.session.commit()

        flash("Profile successfully updated", "success")
        return redirect(f"/users/{user.id}")

    return render_template("users/edit.html",
                            form=form)


@app.route('/users/delete', methods=["POST"])
def delete_user():
    """Delete user."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if g.csrf_form.validate_on_submit():
        do_logout()

        db.session.delete(g.user)
        db.session.commit()

        flash("Profile successfully deleted", "success")
        return redirect("/signup")
    
    return redirect("/")


##############################################################################
# Messages routes:

@app.route('/messages/new', methods=["GET", "POST"])
def message_add():
    """Add a message:

    Show form if GET. If valid, update message and redirect to user page.
    """

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = MessageForm()

    if form.validate_on_submit():
        msg = Message(text=form.text.data)
        g.user.messages.append(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('messages/new.html', form=form)


@app.route('/messages/<int:message_id>', methods=["GET"])
def message_show(message_id):
    """Show a message."""

    msg = Message.query.get(message_id)
    return render_template('messages/show.html', message=msg)


@app.route('/messages/<int:message_id>/delete', methods=["POST"])
def message_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if g.csrf_form.validate_on_submit():
        msg = Message.query.get(message_id)
        db.session.delete(msg)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    flash('Unauthorized form submitted', "danger")
    return redirect('/logout')


@app.route('/messages/<int:message_id>/like', methods=["POST"])
def message_like(message_id):
    """Likes a message for logged in user."""
    
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    if g.csrf_form.validate_on_submit():
        msg = Message.query.get(message_id)
        previous_url = request.referrer

        if msg not in g.user.liked_messages:
            g.user.liked_messages.append(msg)

        else:
            g.user.liked_messages.remove(msg)
        
        db.session.commit()
        return redirect(previous_url)

    flash('Unauthorized form submitted', "danger")
    return redirect('/logout')

##############################################################################
# Homepage and error pages


@app.route('/')
def homepage():
    """Show homepage:

    - anon users: no messages
    - logged in: 100 most recent messages of followed_users
    """

    if g.user:
        followed_user_ids = [user.id for user in g.user.following]
        followed_user_ids.append(g.user.id)
        messages = (Message
                    .query.filter(Message.user_id.in_(followed_user_ids))
                    .order_by(Message.timestamp.desc())
                    .limit(100)
                    .all())

        return render_template('home.html', messages=messages)

    else:
        return render_template('home-anon.html')


##############################################################################
# Turn off all caching in Flask
#   (useful for dev; in production, this kind of stuff is typically
#   handled elsewhere)
#
# https://stackoverflow.com/questions/34066804/disabling-caching-in-flask

@app.after_request
def add_header(response):
    """Add non-caching headers on every request."""

    # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cache-Control
    response.cache_control.no_store = True
    return response
