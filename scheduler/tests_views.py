
from django.contrib.auth.models import User
from django.test import Client, TestCase

def create_user():
	return User.objects.create(
		id=1,
		username='Matt',
		password="password",
		email="email@email.com"
	)

class UsersTestCase(TestCase):
	def test_users_all_status(self):
		c = Client()
		response = c.get('/users/all')
		self.assertEqual(response.status_code, 200)

	def test_users_all(self):
		create_user()
		c = Client()
		response = c.get('/users/all', format='json')
		self.assertEqual(response.data, [{ 'id': 1, 'username': 'Matt', 'email': 'email@email.com'}])