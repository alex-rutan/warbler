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


class UserModelTestCase(TestCase):
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

        self.u = u
        self.u2 = u2

        self.client = app.test_client()

    def test_user_model(self):
        """Does basic model work?"""

        

        # User should have no messages & no followers
        self.assertEqual(len(self.u.messages), 0)
        self.assertEqual(len(self.u.followers), 0)

    def test_is_following(self):
        """Does is_following detect when a user follows another user?"""

        self.u.followers.append(self.u2)
        db.session.commit()

        self.assertEqual(self.u2.is_following(self.u), True)
        self.assertEqual(self.u.is_following(self.u2), False)
        self.assertIn(self.u, self.u2.following)

    def test_is_followed_by(self):
        """Does is_followed_by detect when a user is followed by another user"""

        self.u.following.append(self.u2)

        self.assertEqual(self.u2.is_followed_by(self.u), True)
        self.assertEqual(self.u.is_followed_by(self.u2), False)
        self.assertIn(self.u, self.u2.followers)


