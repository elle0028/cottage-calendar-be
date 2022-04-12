from atexit import register
from http import HTTPStatus
from django.contrib.auth.models import User
from django.db import Error
from rest_framework.test import APIRequestFactory
from rest_framework.test import force_authenticate
from django.test import Client, TestCase, TransactionTestCase
from scheduler.models import Date, Note

from scheduler.views import (
    CustomAuthToken,
    RegisterUser,
    UserViewSet,
    createDate,
    createNote,
    getNonAdminUsers,
)
import logging

logger = logging.getLogger(__name__)

### Utility Functions ###


def create_date():
    return Date.objects.get_or_create(date="2022-02-25")


def create_note():
    return Note.objects.get_or_create(
        id=1, date="2022-02-25", user_id=1, message="This is a test note"
    )


def create_user():
    return User.objects.get_or_create(
        id=1,
        username="Matt",
        password="testPassword1",
        email="email@email.com",
    )


def register_user():
    factory = APIRequestFactory()
    request = factory.post(
        "/register", {"username": "Matt", "password": "testPassword1"}
    )
    view = RegisterUser.as_view()
    response = view(request)


### Test Cases ###


class CreateDateTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        register_user()
        print("SETUP " + str(Date.objects.count()))
        if Date.objects.count() > 0:
            Date.objects.all().delete()

    def tearDown(self):
        if Date.objects.count() > 0:
            Date.objects.all().delete()

    def test_create_date_status(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/date", {"date": "2022-02-25", "user_ids": [], "notes": []}, format="json"
        )
        view = createDate
        user = User.objects.get(username="Matt")
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_create_date_size(self):
        self.assertEqual(Date.objects.count(), 0)
        factory = APIRequestFactory()
        request = factory.post(
            "/date", {"date": "2022-02-25", "user_ids": [], "notes": []}, format="json"
        )
        view = createDate
        user = User.objects.get(username="Matt")
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(Date.objects.count(), 1)


class CreateNoteTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        register_user()
        create_date()

    def tearDown(self):
        if Note.objects.count() > 0:
            Note.objects.all().delete()
        if Date.objects.count() > 0:
            Date.objects.all().delete()

    def test_create_note_status(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/notes",
            {
                "date": "2022-02-25",
                "user_id": 1,
                "message": "This is a test note",
            },
        )
        view = createNote
        user = User.objects.get(username="Matt")
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_create_note_size(self):
        self.assertEqual(Note.objects.count(), 0)
        factory = APIRequestFactory()
        request = factory.post(
            "/notes",
            {
                "date": "2022-02-25",
                "user_id": 1,
                "message": "This is a test note",
            },
        )
        view = createNote
        user = User.objects.get(username="Matt")
        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(Note.objects.count(), 1)


class CustomAuthTokenTestCase(TransactionTestCase):
    reset_sequences = True

    def test_login_user_status(self):
        factory = APIRequestFactory()
        register_user()
        request = factory.post(
            "/login", {"username": "Matt", "password": "testPassword1"}
        )
        view = CustomAuthToken.as_view()
        response = view(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_login_return_token_exists(self):
        register_user()
        factory = APIRequestFactory()
        request = factory.post(
            "/login", {"username": "Matt", "password": "testPassword1"}
        )
        view = CustomAuthToken.as_view()
        response = view(request)
        token = response.data
        self.assertNotEqual(token, None)

    def test_login_400_on_invalid_credentials(self):
        register_user()
        factory = APIRequestFactory()
        view = RegisterUser.as_view()
        request = factory.post("/login", {"username": "Matt", "password": "wrong-pass"})
        response = view(request)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class RegisterUserTestCase(TransactionTestCase):
    reset_sequences = True

    def test_register_user_status(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/register", {"username": "Matt", "password": "testPassword1"}
        )
        view = RegisterUser.as_view()
        response = view(request)
        self.assertEqual(response.status_code, HTTPStatus.CREATED)

    def test_register_user_exists(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/register", {"username": "Matt", "password": "testPassword1"}
        )
        view = RegisterUser.as_view()
        response = view(request)
        user = User.objects.get(username="Matt")
        self.assertNotEqual(user, None)

    def test_register_return_token_exists(self):
        factory = APIRequestFactory()
        request = factory.post(
            "/register", {"username": "Matt", "password": "testPassword1"}
        )
        view = RegisterUser.as_view()
        response = view(request)
        token = response.data
        self.assertNotEqual(token, None)

    def test_register_400_on_duplicate(self):
        factory = APIRequestFactory()
        view = RegisterUser.as_view()
        requestFirst = factory.post(
            "/register", {"username": "Matt", "password": "testPassword1"}
        )
        view(requestFirst)
        requestDuplicate = factory.post(
            "/register", {"username": "Matt", "password": "testPassword1"}
        )
        response = view(requestDuplicate)
        self.assertEqual(response.status_code, HTTPStatus.BAD_REQUEST)


class UsersTestCase(TransactionTestCase):
    reset_sequences = True

    def test_users_all_status(self):
        factory = APIRequestFactory()
        request = factory.get("/users/all")
        create_user()
        user = User.objects.get(username="Matt")
        view = getNonAdminUsers

        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_users_all(self):
        factory = APIRequestFactory()
        request = factory.get("/users/all", format="json")
        create_user()
        user = User.objects.get(username="Matt")
        view = getNonAdminUsers

        force_authenticate(request, user=user)
        response = view(request)
        self.assertEqual(
            response.data,
            [{"id": 1, "username": "Matt", "email": "email@email.com"}],
        )
