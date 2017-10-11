import unittest
import os
import json
from app import create_app, db

class ShoppinglistitemsTestCase(unittest.TestCase):
    """This class represents the shoppinglist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.shoppinglist = {'name': 'vacation'}
        self.shoppinglistitem = {'name': 'Go to Borabora for vacation'}
       

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

    def test_shoppingitem_creation(self):
        """Test API can create a shoppingitem (POST request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        # create a shoppinglistitem by making a POST request
        res = self.client().post(
            '/shoppinglists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglistitem)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_all_shoppingitems_in_a_shoppinglist(self):
        """Test API can get a shoppinglist (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        # create a shoppinglistitem by making a POST request
        res = self.client().post(
            '/shoppinglists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglistitem)
        self.assertEqual(res.status_code, 201)

        # get all the shoppinglistitems in a certain shoppinglist that belong to the test user by making a GET request
        res = self.client().get(
            '/shoppinglists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_one_shoppingitem(self):
        """Test API can get a single shoppinglist by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        

        rv = self.client().post(
            '/shoppinglists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglistitem)

        # assert that the shoppinglist is created 
        self.assertEqual(rv.status_code, 201)
        # get the response data in json format
        results = json.loads(rv.data.decode())

        result = self.client().get(
            '/shoppinglists/items/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the shoppinglist is actually returned given its ID
        self.assertIn('Go to Borabora', str(result.data))

    def test_shoppinglistitem_can_be_edited(self):
        """Test API can edit an existing shoppinglist. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        

        # first, we create a shoppinglist by making a POST request
        rv = self.client().post(
            '/shoppinglists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat pray and love'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the shoppinglist
        results = json.loads(rv.data.decode())

        # then, we edit the created shoppinglist by making a PUT request
        rv = self.client().put(
            '/shoppinglists/items/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Dont just eat but also pray and love "
            })
        self.assertEqual(rv.status_code, 200)

        # finally, we get the edited shoppinglist to see if it is actually edited.
        results = self.client().get(
            '/shoppinglists/items/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Dont just eat', str(results.data))

    def test_shoppinglistitem_deletion(self):
        """Test API can delete an existing shoppingitem. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        # create a shoppinglist by making a POST request
        self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        

        rv = self.client().post(
            '/shoppinglists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'Eat pray and love'})
        self.assertEqual(rv.status_code, 201)
        # get the shoppinglist in json
        results = json.loads(rv.data.decode())

        # delete the shoppinglist we just created
        res = self.client().delete(
            '/shoppinglists/items/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists
        result = self.client().get(
            '/shoppinglists/items/1',
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