"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase

from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler-test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

class MessageModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        u2 = User(
            email="test2@test.com",
            username="testuser2",
            password="HASHED_PASSWORD"
        )

      

        db.session.add_all([u, u2])
        db.session.commit()

        m1 = Message(text='message', user_id=u.id)
        m2 = Message(text='message2', user_id=u.id)

        db.session.add_all([m1, m2])
        db.session.commit()

        self.m1 = m1.id
        self.m2 = m2.id
        self.u = u.id
        self.u2 = u2.id


    def tearDown(self):
        res = super().tearDown()
        db.session.rollback()
        return res


    def test_is_liked_by(self):
        """Does user like this message?"""

        m1 = Message.query.get(self.m1)
        u = User.query.get(self.u)

        m1.liked_by.append(u)

        db.session.commit()

        

        self.assertTrue(m1.is_liked_by(u.username))

    def test_is_liked_by_false(self):
        """Does is_liked_by fail if user not in message.liked_by?"""

        m1 = Message.query.get(self.m1)
        m2 = Message.query.get(self.m2)
        u = User.query.get(self.u)

        m1.liked_by.append(u)

        db.session.commit()

        self.assertFalse(m2.is_liked_by(u.username))