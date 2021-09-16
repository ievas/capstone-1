from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

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
    register_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    current_level_id = db.Column(db.Integer, db.ForeignKey('levels.id'))

    level = db.relationship('Level')
    achievements = db.relationship('UserBadge', backref='user')

    @classmethod
    def register(cls, username, password, email, first_name, last_name, points, current_level_id):

        hashed_password = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username,
            email=email,
            password=hashed_password,
            first_name=first_name,
            last_name = last_name,
            points = points,
            current_level_id = current_level_id
            )

        db.session.add(user)

        return user

    @classmethod
    def authenticate(cls, username, password):
        user = cls.query.filter_by(username=username).first()

        if user:
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user
        return False


class Level(db.Model):
    __tablename__ = 'levels'

    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.Text, nullable=False, unique=True)

    users = db.relationship('User')

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

    achievements = db.relationship('UserBadge', backref="badges")

class UserBadge(db.Model):
    __tablename__ = 'users_badges'
    # do I need a separate combination id
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    badge_id = db.Column(db.Integer, db.ForeignKey('badges.id'), primary_key=True)











def connect_db(app):
    """Connect this database to provided Flask app.

    You should call this in your Flask app.
    """

    db.app = app
    db.init_app(app)