from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy

bcrypt = Bcrypt()
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)
    first_name = db.Column(db.Text, nullable=False)
    last_name = db.Column(db.Text, nullable=False)
    email = db.Column(db.Text, nullable=False, unique=True)
    points = db.Column(db.Integer)
    register_date = db.Column(db.Date)

class Level(db.Model):
    __tablename__ = 'levels'

    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    users = db.relationship('User', secondary="users_levels", backref="levels")

class Streak(db.Model):
    __tablename__ = 'streaks'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # ?
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    last_login_date = db.Column(db.Date)

class Badge(db.Model):
    __tablename__ = 'badges'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)
    icon_url = db.Column(db.Text, nullable=False)

    users = db.relationship('User', secondary="users_badges", backref="badges")

class UserBadge(db.Model):
    __tablename__ = 'users_badges'
    # do I need a seperate combination id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), primary_key=True)

class UserLevel(db.Model):
    __tablename__ = 'users_levels'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    level_id = db.Column(db.Integer, db.ForeignKey('levels.id'), primary_key=True)







def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)