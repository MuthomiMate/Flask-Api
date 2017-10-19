# /tests/test_auth.py

import unittest
import json
from app import create_app, db

class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app(config_name="testing")
        # initialize the test client
        self.client = self.app.test_client
        # This is the user test json data with a predefined email and password
        self.user_data = {
            'email': 'test@example.com',
            'password': 'password123'
        }

        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        """Test user registration works correcty."""
        res = self.client().post('/auth/register', data=self.user_data)
        # get the results returned in json format
        result = json.loads(res.data.decode())
        # assert that the request contains a success message and a 201 status code
        self.assertEqual(result['message'], "You registered successfully. Please log in.")

    def test_empty_email_andpassword_registration(self):
        """Test user email and password are empty"""
        user = {
            'email': '',
            'password': ''
        }
        res = self.client().post('/auth/register', data=user)
        # get the results returned in json format
        result = json.loads(res.data.decode())
        # assert that the request contains a error message
        self.assertEqual(result['message'], "Email, Password and name cannot be empty")
    def test_email_notcorrect_registration(self):
        """Test user email not correct"""
        user = {
            'email': 'muthomi',
            'password': 'muthomi1234'
        }
        res = self.client().post('/auth/register', data=user)
        # get the results returned in json format
        result = json.loads(res.data.decode())
        # assert that the request contains a error message
        self.assertEqual(result['message'], "Enter a correct email address")

    def test_password_not_correct_registration(self):
        """Test user password not correct"""
        user = {
            'email': 'muthomi@mail.com',
            'password': 'muthomi'
        }
        res = self.client().post('/auth/register', data=user)
        # get the results returned in json format
        result = json.loads(res.data.decode())
        # assert that the request contains a error message
        self.assertEqual(result['message'], "Password should be at least 8 characters both numbers and letters")

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        res = self.client().post('/auth/register', data=self.user_data)
        second_res = self.client().post('/auth/register', data=self.user_data)
        # get the results returned in json format
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['message'], "User already exists. Please login.")

    def test_user_login(self):
        """Test registered user can login."""
        res = self.client().post('/auth/register', data=self.user_data)
        login_res = self.client().post('/auth/login', data=self.user_data)

        # get the results in json format
        result = json.loads(login_res.data.decode())
        # Test that the response contains success message
        self.assertEqual(result['message'], "You logged in successfully.")

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post('/auth/login', data=not_a_user)
        # get the result in json
        result = json.loads(res.data.decode())

        # assert that this response must contain an error message
        self.assertEqual(
            result['message'], "Invalid email or password, Please try again")

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
