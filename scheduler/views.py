from django.db import IntegrityError
from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.generics import CreateAPIView
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from scheduler import serializers
from rest_framework.authentication import authenticate

from scheduler.models import Date, Note
from scheduler.serializers import (
    DateSerializer,
    NoteSerializer,
    UserLoginSerializer,
    UserRegisterSerializer,
    UserSerializer,
)
import logging

logger = logging.getLogger(__name__)


@api_view(["GET", "PATCH", "DELETE"])
def getDateById(request, id):
    logger.debug("GET/PUT getDateById", extra={"request": request.data, "id": id})
    try:
        date = Date.objects.get(date=id)
        logger.debug("GOT", extra={"date": date})
    except Date.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = DateSerializer(date, context={"request": request})
        return Response(serializer.data)

    elif request.method == "PATCH":
        serializer = DateSerializer(date, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        date.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def getMonthById(request, year, month):
    searchId = year + "-" + month
    dates = Date.objects.filter(date__startswith=searchId)
    serializer = serializers.DateMonthSerializer(dates, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(["POST"])
def createDate(request):
    logger.debug("POST createDate", extra={"request": request.data})

    serializer = DateSerializer(data=request.data)
    if serializer.is_valid():
        newDate = serializer.save()
        return Response(newDate.date, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def createNote(request):
    logger.debug("POST createNote", extra={"request": request.data})

    serializer = NoteSerializer(data=request.data)
    if serializer.is_valid():
        newNote = serializer.save()
        return Response(newNote.id, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET", "PATCH", "DELETE"])
def getNote(request, id):
    logger.debug("GET/PUT getNote", extra={"request": request.data, "id": id})
    try:
        note = Note.objects.get(pk=id)
        logger.debug("GOT", extra={"note": note})
    except Note.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == "GET":
        serializer = NoteSerializer(note, context={"request": request})
        return Response(serializer.data)

    elif request.method == "PATCH":
        serializer = NoteSerializer(note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == "DELETE":
        note.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(["GET"])
def getNonAdminUsers(request):
    logger.debug("Users", extra={"request": request.headers})
    users = User.objects.exclude(username="admin")
    serializer = serializers.UserSerializer(users, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        logger.debug("GET users", extra={"self": self})
        user = self.request.user
        if user.is_superuser:
            return User.objects.all()
        return User.objects.exclude(username="admin")


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        logger.debug("Login", extra={"request": serializer.validated_data})
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {
                "token": token.key,
                "user_id": user.pk,
            }
        )


class RegisterUser(CreateAPIView):
    permission_classes = (AllowAny,)

    def post(self, request):
        serialized = UserRegisterSerializer(data=request.data)

        if serialized.is_valid():
            logger.debug("Register", extra={"request": serialized.data})
            try:
                user = User.objects.create_user(
                    username=serialized.data["username"],
                    password=serialized.data["password"],
                )
                token, created = Token.objects.get_or_create(user=user)
                return Response(
                    {
                        "token": token.key,
                        "user_id": user.pk,
                    },
                    status=status.HTTP_201_CREATED,
                )
            except IntegrityError:
                return Response(
                    "Username already exists", status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(serialized._errors, status=status.HTTP_400_BAD_REQUEST)
