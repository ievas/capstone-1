# run tests:
#
#    FLASK_ENV=production python -m unittest test_views.py

from unittest import TestCase
import os

# from sqlalchemy import exc
from models import db, connect_db, User, Level, Badge, UserBadge, Guess


os.environ['SQLALCHEMY_DATABASE_URI'] = "postgresql:///panico-test"

# testing model functionality

from app import app, CURRENT_KEY

# db.drop.all()

db.create_all()


app.config['WTF_CSRF_ENABLED'] = False



class UserViewTestCase(TestCase):

    def setUp(self):

        db.drop_all()
        db.create_all()

        User.query.delete()

        self.client = app.test_client()

        self.testuser = User.register(username="testuser",
                                first_name="Anna",
                                last_name="Booo",
                                email="test@test.com",
                                password="testuser",
                                points=0,
                                current_level_id = 1
                        )
        self.testuser_id = 4444
        self.testuser.id = self.testuser_id

        lvl_1 = Level(name="Level_1")
        b = Badge(name='pioneer', icon_url="/static/images/goal.png")

        db.session.add(lvl_1)
        db.session.add(b)
        db.session.commit()



    def tearDown(self):
        response = super().tearDown()
        db.session.rollback()
        return response

    
# test /challenge

    def test_username_shown(self):
        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURRENT_KEY] = self.testuser_id

            resp = c.get("/challenge")

            self.assertIn("testuser", str(resp.data))


    def test_correct_guess(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_KEY] = self.testuser_id
                # ('start.html', form=form, word=word, guess="", word_hint = word_hint, level=level_name)
            
            d = {"word": "blue", "guess": "azul", "translation": "azul"}

            resp = c.post("/challenge", data=d, follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Correct!", str(resp.data))

    def test_wrong_guess(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_KEY] = self.testuser_id
                # ('start.html', form=form, word=word, guess="", word_hint = word_hint, level=level_name)

            d2 = {"word": "blue", "guess": "dog", "translation": "azul"}

            resp = c.post("/challenge", data=d2, follow_redirects=True)
               
            self.assertEqual(resp.status_code, 200)
            self.assertIn("thunder", str(resp.data))

    def test_empty_guess(self):
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURRENT_KEY] = self.testuser_id
                # ('start.html', form=form, word=word, guess="", word_hint = word_hint, level=level_name)

            d3 = {"word": "blue", "guess": "", "translation": "azul"}

            resp = c.post("/challenge", data=d3, follow_redirects=True)
               
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please fill", str(resp.data))

    # test /profile

    def test_badge_shown(self):

        u_b = UserBadge(user_id=self.testuser_id, badge_id=1)

        db.session.add(u_b)
        db.session.commit()

        with self.client as c:

            with c.session_transaction() as sess:
                sess[CURRENT_KEY] = self.testuser_id

            resp = c.get("/profile", follow_redirects=True)

            self.assertIn("Pioneer", str(resp.data))


    # test unauthorized access
    def test_unauthorized_page_access(self):
        with self.client as c:

            resp = c.get("/challenge", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Please sign in or register.", str(resp.data))


