import unittest
import os
import json
from app import create_app, db

class ShoppinglistTestCase(unittest.TestCase):
    """This class represents the shoppinglist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.shoppinglist = {'name': 'Go to Borabora for vacation'}

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self, email="user@test.com", password="test1234"):
        """This helper method helps register a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)

    def test_shoppinglist_creation(self):
        """Test API can create a shoppinglist (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        res = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go to Borabora', str(res.data))

    def test_exists_shoppinglist_creation(self):
        """Test API cannot create a shoppinglist that exists (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        res = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
         #create the same shoppinglist by making a POST request
        res2 = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertIn('That shopping list exists', str(res2.data))

    def test_empty_shoppinglist_creation(self):
        """Test API can create a shoppinglist (POST request)"""
        self.register_user()
        name = {
            'name' : ''
        }
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        res = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=name)
        self.assertIn('Enter name', str(res.data))

    def test_name_with_special_characters_shoppinglist_creation(self):
        """Test API cannot create a shoppinglist with special characters (POST request)"""
        self.register_user()
        name = {
            'name' : '////////'
        }
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        res = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=name)
        self.assertIn('Name should not contain special characters', str(res.data))

    def test_api_can_get_all_shoppinglists(self):
        """Test API can get a shoppinglist (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        res = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        self.assertEqual(res.status_code, 201)

        # get all the shoppinglists that belong to the test user by making a GET request
        res = self.client().get(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_shoppinglist_by_id(self):
        """Test API can get a single shoppinglist by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)

        # assert that the shoppinglist is created 
        self.assertEqual(rv.status_code, 201)
        # get the response data in json format
        results = json.loads(rv.data.decode())

        result = self.client().get(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the shoppinglist is actually returned given its ID
        self.assertEqual(result.status_code, 200)
        self.assertIn('Go to Borabora', str(result.data))

    def test_shoppinglist_can_be_edited(self):
        """Test API can edit an existing shoppinglist. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a shoppinglist by making a POST request
        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the shoppinglist
        results = json.loads(rv.data.decode())

        # then, we edit the created shoppinglist by making a PUT request
        rv = self.client().put(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Dont"
            })
        self.assertEqual(rv.status_code, 200)

    def test_shoppinglist_can_be_edited_with_empty_name(self):
        """Test API can edit  shoppinglist with empty name. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a shoppinglist by making a POST request
        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the shoppinglist
        results = json.loads(rv.data.decode())

        # then, we edit the created shoppinglist by making a PUT request
        rv2 = self.client().put(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": ''
            })
        self.assertIn("Name cannot be empty", str(rv2.data))

    def test_shoppinglist_can_be_edited_with_special_characters(self):
        """Test API can edit  shoppinglist with empty name. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # first, we create a shoppinglist by making a POST request
        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the shoppinglist
        results = json.loads(rv.data.decode())

        # then, we edit the created shoppinglist by making a PUT request
        rv2 = self.client().put(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": '/////'
            })
        self.assertIn("Name should not have special characters", str(rv2.data))

        

    def test_shoppinglist_deletion(self):
        """Test API can delete an existing shoppinglist. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat'})
        self.assertEqual(rv.status_code, 201)
        # get the shoppinglist in json
        results = json.loads(rv.data.decode())

        # delete the shoppinglist we just created
        res = self.client().delete(
            '/shoppinglists/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists
        result = self.client().get(
            '/shoppinglists/1',
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()