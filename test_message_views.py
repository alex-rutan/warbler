"""Message View tests."""

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

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

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


    def test_add_message(self):
        """Test that user can add a message"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            # Now, that session setting is saved, so we can have
            # the rest of ours test

            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)

            msg = Message.query.filter(Message.text == "Hello").one()
            self.assertEqual(msg.text, "Hello")


    def test_display_add_message_form(self):
        """Test that the add message form displays properly"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.get("/messages/new")
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('id="add-message-form"', html)


    def test_cannot_add_message_logged_out(self):
        """Test that user cannot add a message when logged out"""
        
        with self.client as c:

            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)


    def test_show_message(self):
        """Test that the show message route functions properly"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id
        
            resp = c.get(f'/messages/{self.message_id}')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("testmessage", html)

    # TODO: add can/cannot for positive/negative test names for better pattern
    def test_can_delete_message(self):
        """Test that the delete message route functions properly"""
        
        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.testuser.id

            resp = c.post(f'/messages/{self.message_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("testmessage", html)


    def test_cannot_delete_message_other_user(self):
        """Test that a logged in user is prevented from deleting another user's messages"""
        
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

            m1 = Message(text='testmessage', user_id=u.id)

            db.session.add(m1)
            db.session.commit()

            resp = c.get(f'/messages/{m1.id}', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn('<button class="btn btn-outline-danger">Delete</button>', html)


    def test_delete_message_logged_out(self):
        """Test that the delete message route doesn't function properly if logged out"""
        
        with self.client as c:

            resp = c.post(f'/messages/{self.message_id}/delete', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized.", html)


    