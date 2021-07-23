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

from app import app, DEFAULT_IMG

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

        self.u = u.id
        self.u2 = u2.id

        self.client = app.test_client()

    # def tearDown(self):
    #     return super().tearDown()

    def test_user_model(self):
        """Does basic model work?"""

        u = User.query.get(self.u)

        # User should have no messages & no followers
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)


    def test_is_following(self):
        """Does is_following detect when a user follows another user?"""

        u = User.query.get(self.u)
        u2 = User.query.get(self.u2)

        u.followers.append(u2)
        db.session.commit()

        self.assertEqual(u2.is_following(u), True)
        self.assertEqual(u.is_following(u2), False)
        self.assertIn(u, u2.following)


    def test_is_followed_by(self):
        """Does is_followed_by detect when a user is followed by another user"""

        u = User.query.get(self.u)
        u2 = User.query.get(self.u2)

        u.following.append(u2)
        db.session.commit()

        self.assertEqual(u2.is_followed_by(u), True)
        self.assertEqual(u.is_followed_by(u2), False)
        self.assertIn(u, u2.followers)


    def test_signup(self):
        """Does User.signup() successfully create a new user given valid credentials"""

        user3 = User.signup(username = "testuser3", 
                    email = "user3@gmail.com", 
                    password = "password", 
                    image_url = DEFAULT_IMG)

        db.session.add(user3)
        db.session.commit()

        self.assertIn(user3, User.query.all())
        

    def test_signup_failure(self):
        """Does User.signup() fail if not given valid credentials"""

        user3 = User.signup(username = "testuser3", 
                    email = "", 
                    password = "password", 
                    image_url = DEFAULT_IMG)

        db.session.add(user3)
        db.session.commit()

        self.assertRaises(ValueError) 


    def test_authenticate(self):
        """Does User.authenticate successfully return a user when given a valid username and password?"""

        user3 = User.signup(username = "testuser3", 
                    email = "testuser3@gmail.com", 
                    password = "password", 
                    image_url = DEFAULT_IMG)

        db.session.add(user3)
        db.session.commit()

        u3 = User.authenticate(username = user3.username, 
                                    password = "password")
        
        self.assertTrue(u3)


    def test_authenticate_bad_username(self):
        """Does authentication fail with an invalid username?""" 


        authentication_result = User.authenticate(username = 'bad', 
                                    password = 'HASHED_PASSWORD') 


        self.assertFalse(authentication_result)  


    def test_authenticate_bad_password(self):
        """Does authentication fail with an invalid username?""" 

        user3 = User.signup(username = "testuser3", 
                    email = "testuser3@gmail.com", 
                    password = "password", 
                    image_url = DEFAULT_IMG)

        db.session.add(user3)
        db.session.commit()


        authentication_result = User.authenticate                   (username='testuser3',
            password='bad')


        self.assertFalse(authentication_result)  
       






