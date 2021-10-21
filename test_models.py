# run tests:
#
#    FLASK_ENV=production python -m unittest test_models.py

from unittest import TestCase
import os
from sqlalchemy import exc

from models import db, User, Level, Badge, UserBadge, Guess


os.environ['SQLALCHEMY_DATABASE_URI'] = "postgresql:///panico-test"

# testing model functionality

from app import app

# db.drop.all()

db.create_all()

# test User model

class UserModelTestCase(TestCase):
   

    def setUp(self):
        db.drop_all()
        db.create_all()

        # (cls, username, password, email, first_name, last_name, points, current_level_id)

        u1 = User.register("testuser", "testuser", "test@test.com", "Anna", "Booo", 0, 1)
        u1_id = 111
        u1.id = u1_id

        lvl_1 = Level(name="Level_1")
        db.session.add(lvl_1)

        db.session.commit()

        u1 = User.query.get(u1_id)

        self.u1 = u1
        self.u1_id = u1_id

        self.client = app.test_client()

    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response

    def test_user_model(self):

        u = User(username="testuser7", first_name="Hanna", last_name="Fooo", email="b@d.com", password="testuser7", points=0, current_level_id = 1)
        lvl_1 = Level(name="Level_1")

        db.session.add(u)
        # db.session.add(lvl_1)
        db.session.commit()


        self.assertEqual(u.points, 0)
        self.assertEqual(u.current_level_id, 1)

  
    #
    def test_valid__register(self):
         # (cls, username, password, email, first_name, last_name, points, current_level_id)

        u_test = User.register("Baiba3", "999999", "t@g.com", "Baiba", "Fooo", 0, 1)
        uid = 4222
        u_test.id = uid
        db.session.commit()

        u_test = User.query.get(uid)
        self.assertIsNotNone(u_test)
        self.assertEqual(u_test.username, "Baiba3")
        self.assertEqual(u_test.email, "t@g.com")
        self.assertNotEqual(u_test.password, "999999")
        self.assertTrue(u_test.password.startswith("$2b$"))


    def test_invalid_username_register(self):
        no_username = User.register(None, "999999", "t@g.com", "Baiba", "Fooo", 0, 1)
        uid = 898989
        no_username.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()
    # 
    # def test_invalid_email_register

    def test_invalid_email_register(self):
        no_email = User.register("Nadine", "43343334", None, "Baiba", "Rooo", 0, 1)
        uid = 898222
        no_email.id = uid
        with self.assertRaises(exc.IntegrityError) as context:
            db.session.commit()

    # def test_invalid_password_register

    def test_invalid_password_register(self):
        with self.assertRaises(ValueError) as context:
            User.register("Alla", "", "p@g.com", "Alla", "Tooo", 0, 1)

# Authentication
# def authenticate(cls, username, password):

    def test_valid_authentication(self):
        user = User.authenticate(self.u1.username, "testuser")
        self.assertIsNotNone(user)
        self.assertEqual(user.id, self.u1_id)

    def test_invalid_username(self):
        self.assertFalse(User.authenticate("not_username", "testuser"))

    def test_invalid_password(self):
        self.assertFalse(User.authenticate(self.u1.username, "panda"))





    

    