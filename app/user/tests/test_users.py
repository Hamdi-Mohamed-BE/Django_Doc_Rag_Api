import os

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.core import mail

from rest_framework import status
from rest_framework.test import APIClient

from rest_framework_simplejwt.tokens import RefreshToken

from mail.models import Mail
from user.models import User

CURR_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_FILES_DIR = os.path.join(CURR_DIR, "test_files")

RESISTER_USER_URL = reverse("user:email_registration")
AUTH_USER_URL = reverse("user:token_obtain_email")
REFRESH_TOKEN_URL = reverse("user:token_refresh")
USER_DETAIL_URL = reverse("user:detail")

UPDATE_USER_URL = reverse("user:update")
UPDATE_LOCATION_URL = reverse("user:update_location")
UPDATE_AVATAR_URL = reverse("user:avatar")

PASSWORD_CHANGE_URL = reverse("user:password_change")
EMAIL_VERIFY_REQUEST_URL = reverse("user:send_verify_email")
EMAIL_VERIFY_SUBMIT_URL = reverse("user:verify_email")
PASSWORD_RESET_REQUEST_URL = reverse("user:password_reset_request")
PASSWORD_RESET_SUBMIT_URL = reverse("user:password_reset_submit")

GOOGLE_AUTH_URL = reverse("user:oauth_google")
FACEBOOK_AUTH_URL = reverse("user:oauth_facebook")
APPLE_AUTH_URL = reverse("user:oauth_apple")
INSTAGRAM_AUTH_URL = reverse("user:oauth_instagram")

DELETE_ME_URL = reverse("user:delete_me")

SEND_MAIL_VERIFY_URL = reverse("user:send_verify_email")
SUBMIT_MAIL_VERIFY_URL = reverse("user:verify_email")

def create_user(**params):
    return get_user_model().objects.create_user(**params)


class UserApiTests(TestCase):
    """Test the users API. For coverage use: coverage run --omit=*/migrations/* manage.py test user"""

    def setUp(self):
        self.client = APIClient()

    #------------------- User Registration and Authentication -------------------#
    def test_registration_email_success(self):
        """Test registering a user with an email is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
        }
        res = self.client.post(RESISTER_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_registration_email_user_exists(self):
        """Test registering a user that already exists fails"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'name': 'Test Name'
        }
        create_user(**payload)
        res = self.client.post(RESISTER_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_registration_email_password_too_short(self):
        """Test that the password must be more than 8 characters"""
        payload = {
            'email': 'test@example.com',
            'password': 'pw',
        }
        res = self.client.post(RESISTER_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    #------------------- User Authentication -------------------#
    def test_login_email_success(self):
        """Test logging in with email is successful"""
        payload = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        create_user(**payload)
        res = self.client.post(AUTH_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', res.data)
        self.assertIn('refresh', res.data)

    def test_login_email_invalid_credentials(self):
        """Test logging in with invalid credentials fails"""
        create_user(email='test@example.com', password='testpass123')
        payload = {
            'email': 'test@example.com',
            'password': 'wrongpass'
        }
        res = self.client.post(AUTH_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)

    def test_login_email_nonexistent_user(self):
        """Test logging in with a nonexistent user fails"""
        payload = {
            'email': 'nonexistent@example.com',
            'password': 'testpass123'
        }
        res = self.client.post(AUTH_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', res.data)
        self.assertNotIn('refresh', res.data)

    def test_refresh_token_success(self):
        """Test refreshing the token is successful"""
        user = create_user(email='test@example.com', password='testpass123')
        refresh = RefreshToken.for_user(user)
        payload = {
            'refresh': str(refresh)
        }
        res = self.client.post(REFRESH_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', res.data)

    def test_refresh_token_invalid(self):
        """Test refreshing the token with an invalid token fails"""
        payload = {
            'refresh': 'invalidtoken'
        }
        res = self.client.post(REFRESH_TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', res.data)

    #------------------- User Detail -------------------#
    def test_retrieve_user_detail_success(self):
        """Test retrieving user detail for logged in user"""
        user = create_user(email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)
        res = self.client.get(USER_DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['email'], user.email)

    def test_retrieve_user_detail_unauthorized(self):
        """Test that authentication is required for user detail"""
        res = self.client.get(USER_DETAIL_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    #------------------- User Update -------------------#
    def test_update_user_success(self):
        """Test updating the user profile for authenticated user"""
        user = create_user(email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)
        payload = {'name': 'new name',}

        res = self.client.patch(UPDATE_USER_URL, payload)

        user.refresh_from_db()
        self.assertEqual(user.name, payload['name'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        payload = {
            "email": "user2@example.com",
            "name": "new name",
            "surname": "new surname",
            "send_push_notifications": False
        }
        res = self.client.patch(UPDATE_USER_URL, payload)

        user.refresh_from_db()
        self.assertEqual(user.email, payload['email'])
        self.assertEqual(user.name, payload['name'])
        self.assertEqual(user.surname, payload['surname'])
        self.assertEqual(user.send_push_notifications, payload['send_push_notifications'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)
    
    #------------------- Update Location -------------------#
    def test_update_location_success(self):
        """Test updating the user's location for authenticated user"""
        user = create_user(email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)
        payload = {
            'current_location': {
                'longitude': 12.34,
                'latitude': 56.78
            }
        }

        res = self.client.patch(UPDATE_LOCATION_URL, payload, format='json')

        user.refresh_from_db()
        self.assertEqual(user.current_location.x, payload['current_location']['longitude'])
        self.assertEqual(user.current_location.y, payload['current_location']['latitude'])
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # verify with details api
        res = self.client.get(USER_DETAIL_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['current_location']['longitude'], payload['current_location']['longitude'])
        self.assertEqual(res.data['current_location']['latitude'], payload['current_location']['latitude'])

    #------------------- Update Avatar -------------------#
    def test_update_avatar_success(self):
        """Test updating the user's avatar for authenticated user"""
        user = create_user(email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)

        # call details api and make sure that avatar is None
        res = self.client.get(USER_DETAIL_URL)  
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNone(res.data['avatar'])
        
        with open(os.path.join(TEST_FILES_DIR, 'test_avatar.jpg'), 'rb') as avatar:
            payload = {'avatar': avatar}
            res = self.client.patch(UPDATE_AVATAR_URL, payload, format='multipart')

        user.refresh_from_db()
        self.assertTrue(user.avatar)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # call details api and make sure that avatar is not None
        res = self.client.get(USER_DETAIL_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(res.data['avatar'])

        #------------------- Change Password -------------------#
    
    #------------------- Change Password -------------------#
    def test_change_password_success(self):
        """Test changing the user's password for authenticated user"""
        user = create_user(email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)
        payload = {
            'old_password': 'testpass123',
            'new_password': 'newpassword123'
        }

        res = self.client.post(PASSWORD_CHANGE_URL, payload)

        user.refresh_from_db()
        self.assertTrue(user.check_password(payload['new_password']))
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
    
    def test_change_password_fail(self):
        """Test changing the user's password with incorrect old password fails"""
        user = create_user(email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)
        payload = {
            'old_password': 'wrongoldpassword',
            'new_password': 'newpassword123'
        }

        res = self.client.post(PASSWORD_CHANGE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertTrue(user.check_password('testpass123'))

    def test_change_password_same_as_old(self):
        """Test changing the user's password to the same as the old password fails"""
        user = create_user(email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)
        payload = {
            'old_password': 'testpass123',
            'new_password': 'testpass123'
        }

        res = self.client.post(PASSWORD_CHANGE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertTrue(user.check_password('testpass123'))

    def test_change_password_too_short(self):
        """Test changing the user's password to a short password fails"""
        user = create_user(email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)
        payload = {
            'old_password': 'testpass123',
            'new_password': 'pw'
        }

        res = self.client.post(PASSWORD_CHANGE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user.refresh_from_db()
        self.assertTrue(user.check_password('testpass123'))

    
    #------------------- Delete User -------------------#
    def test_delete_user_success(self):
        """Test deleting the authenticated user"""
        user = create_user(email='test@example.com', password='testpass123')
        self.client.force_authenticate(user=user)

        res = self.client.delete(DELETE_ME_URL)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        user_exists = get_user_model().objects.filter(email=user.email).exists()
        self.assertFalse(user_exists)

# to run this test: python manage.py test user.tests.test_users.UserApiTests