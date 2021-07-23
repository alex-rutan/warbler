"""User View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app, CURR_USER_KEY, DEFAULT_IMG

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False

class UserViewTestCase(TestCase):
    """Test views for users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

# TESTUSER VARIABLE SHOULD MATCH PREVIOUS TESTS(U, U2 ETC.)
        self.testuser = User.signup(username="testuser",
                                    email="test@test.com",
                                    password="testuser",
                                    image_url=None)

        db.session.commit()

        self.testuser_id = self.testuser.id

        self.message = Message(text = "testmessage",
                                user_id = self.testuser.id)
        
        db.session.add(self.message)
        db.session.commit()

        self.message_id = self.message.id


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_show_following(self):
        """Test that you can see a different user's following page"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            
            u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            image_url = DEFAULT_IMG)

            db.session.commit()

            resp = c.get(f'/users/{u2.id}/following')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="followed-user-container"', html)
            # TODO could test that username is in the html - protects against changes to id in the future


    def test_show_followers(self):
        """Test that you see a different user's followers page"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
            
            u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            image_url = DEFAULT_IMG)

            db.session.commit()

            resp = c.get(f'/users/{u2.id}/followers')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="following-user-container"', html)


    def test_show_followers_logged_out(self):
        """Test that you can't see a user's followers page when logged out"""

        with self.client as c:
            
            u2 = User.signup(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD",
            image_url = DEFAULT_IMG)

            db.session.commit()

            resp = c.get(f'/users/{u2.id}/followers')

            self.assertEqual(resp.status_code, 302)

    
    def test_update_other_user(self):
        """Test that a logged in user is prevented from updating another user's profile"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            u = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
            )

            db.session.add(u)
            db.session.commit()

            resp = c.get(f"/users/{u.id}")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('id="edit-user-btn"', html)
