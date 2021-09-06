from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
import requests
import random
import os
import time

from models import db, connect_db, User, Level, Streak, Badge
from forms import TranslationForm, RegisterForm, SignInForm

from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///panico"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "las palabras"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False


CURRENT_KEY = "curr_user"

API_BASE_URL = "https://www.dictionaryapi.com/api/v3/references/spanish/json/"

AUDIO_BASE_URL = "https://media.merriam-webster.com/audio/prons/es/me/mp3"

# https://media.merriam-webster.com/audio/prons/[language_code]/[country_code]/[format]/[subdirectory]/[base filename].[format]

# "https://media.merriam-webster.com/audio/prons/es/me/mp3/s/salt0001.mp3"



KEY = os.environ.get('API_KEY')

connect_db(app)

toolbar = DebugToolbarExtension(app)
###################################################


def read_words(path):
    """return words from the level dictionary"""

    level_dictionary = open(path)

    words = [w.strip() for w in level_dictionary]
    level_dictionary.close()
    return words


def get_a_word():

    words = read_words("words_lvl_1.txt")

    word = random.choice(words)

    return word




def translate_a_word(word):
    res = requests.get(f"{API_BASE_URL}/{word}", params={'key':KEY})

    data = res.json()

    shortdef = data[0]['shortdef'][0]

    # meta_shortdef = data[0]['shortdef'][0]

    # sound_file_name = data[0]['hwi']['prs'][0]['sound'][0]

    translation = shortdef.split(",")[0]

    return translation

# *********************************
@app.before_request
def add_user_to_global():
    if CURRENT_KEY in session:
        g.user = User.query.get(session[CURRENT_KEY])

    else:
        g.user = None

def signin(user):
    """Sign in."""

    session[CURRENT_KEY] = user.id

def signout():
    """Sign out."""
    if CURRENT_KEY in session:
        del session[CURRENT_KEY]


# ************************************************************************

@app.route('/')
def home():
    """Home page."""

    return render_template('home.html')


@app.route('/register')
def show_register_form():
    form = RegisterForm()
    return render_template('register.html', form = form)


@app.route('/register', methods=["POST"])
def register():
    if CURRENT_KEY in session:
        del session[CURRENT_KEY]

    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = User.register(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data,
                first_name = form.first_name.data,
                last_name = form.last_name.data,
                points = 0,
            )

            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('/register.html', form=form)
        
        signin(user)

        return redirect("/")
    else:
        return redirect('/register', form=form)

@app.route('/signin')
def show_sign_in():
    """Show log in form"""

    form = SignInForm()

    return render_template("/signin.html", form=form)


@app.route('/signin', methods=["POST"])
def sign_in():
    """Handle login"""

    form = SignInForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            signin(user)
            return redirect("/challenge")

    return render_template('/signin.html', form = form)

@app.route('/signout')
def logout():
    """Handle logout"""
    signout()

    flash("You have successfully signed out.", 'success')
    return redirect("/")



@app.route('/challenge', methods=["GET"])
def challenge_page():
    """Get a challenge"""
    word = get_a_word()

    form = TranslationForm(word=word)
    
    # word_and_translation = translate_a_word()

    
    return render_template('start.html', form=form, word=word, guess="")
 


# get /challenge -> challenge.html
# post /check_translation -> result.html

@app.route('/challenge', methods=["POST"])

def check_answer():
  """Handle user input"""
  form = TranslationForm()
  if form.validate_on_submit():
    guess = form.translation.data

    word = request.form.get('word')

    translation = translate_a_word(word)

    return render_template('check.html', form=form, word=word, guess=guess, translation=translation)
  
  else:
    word = get_a_word()
    form = TranslationForm(word=word)
    return render_template('start.html', word=word, form=form)


# @app.route('/progress')



    

    

    
