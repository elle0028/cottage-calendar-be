from atexit import register
from datetime import date
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
    getDateById,
    getMonthById,
    getNonAdminUsers,
    getNote,
)
import logging

logger = logging.getLogger(__name__)

### Utility Functions ###


def create_date():
    return Date.objects.get_or_create(date="2022-02-25")


def create_note(date):
    return Note.objects.get_or_create(
        id=1, date=date, user_id=1, message="This is a test note"
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


class DatePatchTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        create_user()

    def test_patch_date_does_not_exist(self):
        date_id = "2022-02-25"
        factory = APIRequestFactory()
        request = factory.delete("date/" + date_id)
        user = User.objects.get(username="Matt")
        view = getDateById

        force_authenticate(request, user=user)
        response = view(request, date_id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_patch_date_status_ok(self):
        date_id = "2022-02-25"
        factory = APIRequestFactory()
        create_date()
        request = factory.patch(
            "date/" + date_id, {"date": date_id, "user_ids": [1]}, format="json"
        )
        user = User.objects.get(username="Matt")
        view = getDateById

        force_authenticate(request, user=user)
        response = view(request, date_id)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_patch_date(self):
        date_id = "2022-02-25"
        factory = APIRequestFactory()
        create_date()
        request = factory.patch(
            "date/" + date_id, {"date": date_id, "user_ids": [1]}, format="json"
        )
        user = User.objects.get(username="Matt")
        view = getDateById

        force_authenticate(request, user=user)
        response = view(request, date_id)
        date = Date.objects.get(date=date_id)
        self.assertEqual(date.date, date_id)
        self.assertEqual(date.users.get(username="Matt"), user)


class DateDeleteTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        create_user()

    def test_delete_date_does_not_exist(self):
        date_id = "2022-02-25"
        factory = APIRequestFactory()
        request = factory.delete("date/" + date_id)
        user = User.objects.get(username="Matt")
        view = getDateById

        force_authenticate(request, user=user)
        response = view(request, date_id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_date_status(self):
        date_id = "2022-02-25"
        factory = APIRequestFactory()
        request = factory.delete("date/" + date_id)
        user = User.objects.get(username="Matt")
        view = getDateById
        create_date()

        force_authenticate(request, user=user)
        response = view(request, date_id)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_delete_date(self):
        date_id = "2022-02-25"
        factory = APIRequestFactory()
        request = factory.delete("date/" + date_id)
        user = User.objects.get(username="Matt")
        view = getDateById
        create_date()
        self.assertEqual(Date.objects.all().count(), 1)

        force_authenticate(request, user=user)
        response = view(request, date_id)
        self.assertEqual(Date.objects.all().count(), 0)


class DateGetTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        create_user()

    def test_get_date_does_not_exist(self):
        date_id = "2022-02-25"
        factory = APIRequestFactory()
        request = factory.get("date/" + date_id)
        user = User.objects.get(username="Matt")
        view = getDateById

        force_authenticate(request, user=user)
        response = view(request, date_id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_get_date_status(self):
        date_id = "2022-02-25"
        factory = APIRequestFactory()
        request = factory.get("date/" + date_id)
        user = User.objects.get(username="Matt")
        view = getDateById
        create_date()

        force_authenticate(request, user=user)
        response = view(request, date_id)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_date(self):
        date_id = "2022-02-25"
        factory = APIRequestFactory()
        request = factory.get("date/" + date_id)
        user = User.objects.get(username="Matt")
        view = getDateById
        create_date()

        force_authenticate(request, user=user)
        response = view(request, date_id)
        self.assertEqual(response.data, {"date": date_id, "users": [], "notes": []})


class MonthTestCase(TransactionTestCase):
    reset_sequences = True
    year = "2022"
    month = "02"
    month_url = "/month/" + year + "/" + month

    def setUp(self):
        create_user()

    def test_get_month_status(self):
        factory = APIRequestFactory()
        request = factory.get(self.month_url)
        user = User.objects.get(username="Matt")
        view = getMonthById

        force_authenticate(request, user=user)
        response = view(request, self.year, self.month)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_month_empty(self):
        factory = APIRequestFactory()
        request = factory.get(self.month_url)
        user = User.objects.get(username="Matt")
        view = getMonthById

        force_authenticate(request, user=user)
        response = view(request, self.year, self.month)
        self.assertEqual(response.data, [])

    def test_get_month_with_date(self):
        factory = APIRequestFactory()
        request = factory.get(self.month_url)
        create_date()
        user = User.objects.get(username="Matt")
        view = getMonthById

        force_authenticate(request, user=user)
        response = view(request, self.year, self.month)
        self.assertEqual(response.data, [{"date": "2022-02-25", "users": []}])


class NotePatchTestCase(TransactionTestCase):
    reset_sequences = True
    note_msg = "Patched Message"
    date_id = "2022-02-25"

    def setUp(self):
        create_user()
        create_date()

    def create_note(self):
        date = Date.objects.get(date=self.date_id)
        create_note(date)

    def test_patch_note_does_not_exist(self):
        note_id = 1
        factory = APIRequestFactory()
        request = factory.delete("note/" + str(note_id))
        user = User.objects.get(username="Matt")
        view = getNote

        force_authenticate(request, user=user)
        response = view(request, note_id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_patch_note_status_ok(self):
        note_id = 1
        factory = APIRequestFactory()
        self.create_note()
        request = factory.patch(
            "note/" + str(note_id), {"message": self.note_msg}, format="json"
        )
        user = User.objects.get(username="Matt")
        view = getNote

        force_authenticate(request, user=user)
        response = view(request, note_id)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_patch_note(self):
        note_id = 1
        factory = APIRequestFactory()
        self.create_note()
        request = factory.patch(
            "note/" + str(note_id), {"message": self.note_msg}, format="json"
        )
        user = User.objects.get(username="Matt")
        view = getNote

        force_authenticate(request, user=user)
        response = view(request, note_id)
        note = Note.objects.get(pk=note_id)
        self.assertEqual(note.message, self.note_msg)


class NoteDeleteTestCase(TransactionTestCase):
    reset_sequences = True
    date_id = "2022-02-25"

    def setUp(self):
        create_user()
        create_date()

    def create_note(self):
        date = Date.objects.get(date=self.date_id)
        create_note(date)

    def test_delete_note_does_not_exist(self):
        note_id = 1
        factory = APIRequestFactory()
        request = factory.delete("note/" + str(note_id))
        user = User.objects.get(username="Matt")
        view = getNote

        force_authenticate(request, user=user)
        response = view(request, note_id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_delete_note_status(self):
        note_id = 1
        factory = APIRequestFactory()
        request = factory.delete("note/" + str(note_id))
        user = User.objects.get(username="Matt")
        view = getNote
        self.create_note()

        force_authenticate(request, user=user)
        response = view(request, note_id)
        self.assertEqual(response.status_code, HTTPStatus.NO_CONTENT)

    def test_delete_note(self):
        note_id = 1
        factory = APIRequestFactory()
        request = factory.delete("note/" + str(note_id))
        user = User.objects.get(username="Matt")
        view = getNote
        self.create_note()
        self.assertEqual(Note.objects.all().count(), 1)

        force_authenticate(request, user=user)
        response = view(request, note_id)
        self.assertEqual(Note.objects.all().count(), 0)


class NoteGetTestCase(TransactionTestCase):
    reset_sequences = True
    date_id = "2022-02-25"

    def setUp(self):
        create_user()
        create_date()

    def create_note(self):
        date = Date.objects.get(date=self.date_id)
        create_note(date)

    def test_get_note_does_not_exist(self):
        note_id = 1
        factory = APIRequestFactory()
        request = factory.get("note/" + str(note_id))
        user = User.objects.get(username="Matt")
        view = getNote

        force_authenticate(request, user=user)
        response = view(request, note_id)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_get_note_status(self):
        note_id = 1
        factory = APIRequestFactory()
        self.create_note()
        request = factory.get("note/" + str(note_id))
        user = User.objects.get(username="Matt")
        view = getNote

        force_authenticate(request, user=user)
        response = view(request, note_id)
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_get_note(self):
        note_id = 1
        factory = APIRequestFactory()
        request = factory.get("note/" + str(note_id))
        user = User.objects.get(username="Matt")
        view = getNote
        self.create_note()

        note = Note.objects.get(pk=note_id)

        force_authenticate(request, user=user)
        response = view(request, note_id)
        self.assertEqual(response.data["id"], 1)
        self.assertEqual(response.data["message"], "This is a test note")
        self.assertEqual(response.data["user"]["id"], 1)


class CreateDateTestCase(TransactionTestCase):
    reset_sequences = True

    def setUp(self):
        register_user()

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
