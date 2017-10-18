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

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log and register in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        self.client().post('/auth/register', data=user_data)
        result = self.client().post('/auth/login', data=user_data)
        access_token = json.loads(result.data.decode())['access_token']
        return access_token

    def create_shoppinglistitem(self):
        """
        create a shopping list fior a user
        """
        
        access_token = self.login_user()

        # create a shoppinglist by making a POST request
        self.client().post(
            '/shoppinglists/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglist)
        # create shopping list items
        return self.client().post(
            '/shoppinglists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.shoppinglistitem)

    def test_shoppingitem_creation(self):
        """Test API can create a shoppingitem (POST request)"""
        res = self.create_shoppinglistitem()
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_all_shoppingitems_in_a_shoppinglist(self):
        """Test API can get a shoppinglist (GET request)."""
        access_token = self.login_user()
        self.create_shoppinglistitem()

        # get all the shoppinglistitems in a certain shoppinglist that belong to the test user by making a GET request
        res = self.client().get(
            '/shoppinglists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertIn('Go to Borabora', str(res.data))

    def test_api_can_get_one_shoppingitem(self):
        """Test API can get a single shoppinglist by using it's id."""
        access_token = self.login_user()
        self.create_shoppinglistitem()
        result = self.client().get(
            '/shoppinglists/items/1',
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the shoppinglist is actually returned given its ID
        self.assertIn('Go to Borabora', str(result.data))
    def test_api_can_get_nonexisting_shoppingitem(self):
        """Test API can get a single shoppinglist by using it's id."""
        access_token = self.login_user()
        result = self.client().get(
            '/shoppinglists/items/10',
            headers=dict(Authorization="Bearer " + access_token))
        # assert that the shoppinglist is actually returned given its ID
        self.assertIn('That item does not exist', str(result.data))

    def test_shoppinglistitem_can_be_edited(self):
        """Test API can edit an existing shoppinglist. (PUT request)"""
        access_token = self.login_user()
        self.create_shoppinglistitem()

        # then, we edit the created shoppinglist by making a PUT request
        rv = self.client().put(
            '/shoppinglists/items/1',
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": "Dont just eat but also pray and love "
            })
        self.assertIn('Dont just eat', str(rv.data))
    def test_shoppinglistitem_can_be_edited_with_no_name(self):
        """Test API can edit an existing shoppinglist. (PUT request)"""
        access_token = self.login_user()
        self.create_shoppinglistitem()

        # then, we edit the created shoppinglist by making a PUT request
        rv = self.client().put(
            '/shoppinglists/items/1',
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": ''
            })
        self.assertIn('Name cannot be empty', str(rv.data))

    def test_shoppinglistitem_can_be_edited_with_existing_name(self):
        """Test API can edit an existing shoppinglist. (PUT request)"""
        access_token = self.login_user()
        self.create_shoppinglistitem()
        rv = self.client().post(
            '/shoppinglists/1/items/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'name': 'pray'})
        results = json.loads(rv.data.decode())

        # then, we edit the created shoppinglist by making a PUT request
        rv = self.client().put(
            '/shoppinglists/items/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "name": 'Go to Borabora for vacation'
            })
        self.assertIn('shopping item with that name exist', str(rv.data))

    def test_shoppinglistitem_deletion(self):
        """Test API can delete an existing shoppingitem. (DELETE request)."""
        access_token = self.login_user()
        self.create_shoppinglistitem()

        # delete the shoppinglist we just created
        res = self.client().delete(
            '/shoppinglists/items/1',
            headers=dict(Authorization="Bearer " + access_token),)
        self.assertEqual(res.status_code, 200)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()