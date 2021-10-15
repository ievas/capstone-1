from flask import Flask, render_template, request, flash, redirect, session, g
from flask_debugtoolbar import DebugToolbarExtension
import requests
import random
import os
import time

from models import db, connect_db, User, Level, Streak, Badge, UserBadge, Guess
from forms import TranslationForm, RegisterForm, SignInForm

from sqlalchemy.exc import IntegrityError


app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///panico"
# app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
#     'DATABASE_URL').replace("://", "ql://",1)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
# app.config["SECRET_KEY"] = "las palabras"
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'las palabras')
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


def get_a_word(curr_level):

    words = read_words(f"words_lvl_{curr_level}.txt")

    word = random.choice(words)

    if word != None:
        return word
    else:
        word = random.choice(words)



def translate_a_word(word):
    
    res = requests.get(f"{API_BASE_URL}/{word}", params={'key':KEY})
    print(res)
    data = res.json()

    shortdef = data[0]['shortdef'][0]

    # meta_shortdef = data[0]['shortdef'][0]

    # sound_file_name = data[0]['hwi']['prs'][0]['sound'][0]

    translation = shortdef.split(",")[0]
    translation = translation.split(" ")[0]

    return translation


def make_a_hint(string):
    
    str_len = len(string)
    hint = ""

    for idx, char in enumerate(string):
        if idx == 0:
            hint += char
        elif idx != (str_len-1):
            hint += " _ "
        else:
            hint += string[str_len -1]

    return hint


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

    if g.user:
        current_level = g.user.current_level_id
        all_words = read_words(f"words_lvl_{current_level}_esp.txt")
        return render_template('home.html', level = current_level, words = all_words, clean_footer="oh, yes")

    return render_template('home.html', clean_footer="oh, yes")


@app.route('/register')
def show_register_form():
    form = RegisterForm()
    return render_template('register.html', form = form, clean_footer="oh, yes")


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
                current_level_id = 1
            )
            db.session.commit()

        except IntegrityError as e:
            flash("Username already taken", 'danger')
            return render_template('/register.html', form=form, clean_footer="oh, yes")

        # user_level = UserLevel(user_id = user.id, level_id = 1)

        # db.session.add_all([user_level])
        # db.session.commit()
        
        signin(user)

        return redirect("/")
    else:
        return redirect('/register')

@app.route('/signin')
def show_sign_in():
    """Show log in form"""

    form = SignInForm()

    return render_template("/signin.html", form=form, clean_footer="oh, yes")


@app.route('/signin', methods=["POST"])
def sign_in():
    """Handle login"""

    form = SignInForm()

    if form.validate_on_submit():
        user = User.authenticate(form.username.data, form.password.data)

        if user:
            signin(user)
            return redirect("/")

    return render_template('/signin.html', form = form, clean_footer="oh, yes")

@app.route('/signout')
def logout():
    """Handle logout"""
    signout()

    flash("You have successfully signed out.", 'success')
    return redirect("/")



@app.route('/challenge', methods=["GET"])
def challenge_page():
    """Get a challenge"""
    # find out the level
    user = User.query.get(session[CURRENT_KEY])
    # word = get_a_word(user.current_level_id)
        
    while True:
        
        word = get_a_word(user.current_level_id)
        word_guessed = Guess.query.filter(Guess.user_id == user.id, Guess.word == word, Guess.is_correct == True).first()

        if word_guessed is None:
            break
        else:
            print("THIS WAS ALREADY GUESSED CORRECTLY: " + word)

    form = TranslationForm(word=word)

    # while word_guessed

    translation = translate_a_word(word)

    word_hint = make_a_hint(translation)

    user = User.query.get(session[CURRENT_KEY])

    curr_level_id = user.current_level_id

    level_name = Level.query.get(curr_level_id).name

    return render_template('start.html', form=form, word=word, guess="", word_hint = word_hint, level=level_name)
 

@app.route('/challenge', methods=["POST"])

def check_answer():
  """Handle user input"""

  form = TranslationForm()

 
  if form.validate_on_submit():

    guess = form.translation.data

    guess = guess.lower()

    word = request.form.get('word')

    translation = translate_a_word(word)

    if g.user:

        user = User.query.get(session[CURRENT_KEY])

        if guess == translation:

            if Guess.query.filter(Guess.word == word, Guess.user_id == user.id, Guess.is_correct == False).first():
                guess_to_update = Guess.query.filter_by(word = word).first()
                guess_to_update.is_correct = True
                db.session.commit()

            elif Guess.query.filter(Guess.word == word, Guess.user_id == user.id, Guess.is_correct == True).first() is None:
                # print("YES, IT IS NONE. THAT MEANS I CAN'T FIND IT." + word)
                correct_guess = Guess(word = word, user_id = user.id, is_correct = True)
                db.session.add(correct_guess)
                db.session.commit()

            # correct_guess = Guess(word = guess, user_id = user.id, is_correct = True)
            # wrong_guess = Guess.query.filter_by()
            # if word already in the table, then update
            # db.session.add(correct_guess)

            if user.points < 15:
                user.points = user.points + 1
            else:
                user.points = 15

            db.session.commit()
            
            if user.points == 3:
                
                flash("You earned the Pioneer badge and move to Level 2!", "success")
                badge = Badge.query.filter_by(name='pioneer').first()
                user.current_level_id = user.current_level_id + 1
                pioneer_badge = UserBadge(user_id=user.id, badge_id=badge.id)
                db.session.add(pioneer_badge)
                db.session.commit()

            if user.points == 6:
                flash("Great work! You move to Level 3.", "success")
                user.current_level_id = user.current_level_id + 1
                db.session.commit()
            
            if user.points == 9:
                flash("You earned the Prodigy badge!", "success")
                badge = Badge.query.filter_by(name='prodigy').first()
                prodigy_badge = UserBadge(user_id=user.id, badge_id=badge.id)
                db.session.add(prodigy_badge)
                db.session.commit()
            if user.points == 15:
                flash("Finish line: You've learned 15 words!", "success")
                badge = Badge.query.filter_by(name='finish').first()
                if UserBadge.query.filter(UserBadge.user_id == user.id, UserBadge.badge_id == badge.id).first() is None:
                    finish_badge = UserBadge(user_id=user.id, badge_id=badge.id)
                    db.session.add(finish_badge)
                    db.session.commit()
                return render_template('finish.html', clean_footer="oh, yes")
        else:
            if Guess.query.filter(Guess.word == word, Guess.is_correct == False).first() is None:
                wrong_guess = Guess(word = word, user_id = user.id, is_correct = False)
                db.session.add(wrong_guess)
                db.session.commit()

    return render_template('start.html', form=form, word=word, guess=guess, translation=translation)
    # return redirect("/challenge/" + translation)
  
  else:
    
    flash("Please fill out the field.", "danger")
    # user = User.query.get(session[CURRENT_KEY])
    word = request.form.get('word')
    form = TranslationForm(word=word)
    return render_template('start.html', word=word, form=form)

# @app.route('/challenge/<word>')
# def solution(word):

#     return render_template('check.html', form=form, word=word, guess=guess, translation=translation)


@app.route('/profile')

def show_user_details():
    """Show user profile information and progress"""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    
    user = User.query.get(session[CURRENT_KEY])

    curr_level_id = user.current_level_id

    level_name = Level.query.get(curr_level_id).name

    user_badges = UserBadge.query.filter_by(user_id=user.id).all()


    badge_list = []
    icon_list = []

    for obj in user_badges:
        badge_list.append(Badge.query.get(obj.badge_id).name)
        icon_list.append(Badge.query.get(obj.badge_id).icon_url)
        print(badge_list)

    # badges = Badge.query.filter_by(id = user_badges).all()


    return render_template('details.html', user=user, level = level_name, badges=badge_list, icons=icon_list, clean_footer="oh, yes")


@app.route('/reset', methods=["GET","POST"])

def reset():
    user = User.query.get(session[CURRENT_KEY])
    UserBadge.query.delete()
    Guess.query.delete()
    user.current_level_id = 1
    user.points = 0
    db.session.commit()

    return redirect("/challenge")




    

    

    
