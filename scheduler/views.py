from django.shortcuts import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import AllowAny
from scheduler import serializers
from scheduler.models import Date, Note
from scheduler.serializers import (
    DateSerializer,
    NoteSerializer,
    UserLoginSerializer,
    UserSerializer,
)
import logging

logger = logging.getLogger(__name__)


def index(request):
    return HttpResponse("Hello World")


class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]


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


class Login(APIView):
    permission_classes = ()
    authentication_classes = ()

    def post(self, request):
        logger.debug("Login", extra={"request": request.data})
        logger.debug("Login", extra={"request": request.data})

        username = request.data.get("username", None)
        password = request.data.get("password", None)
        if username and password:
            user_obj = User.objects.filter(username=username)
            logger.debug("Users", extra={"user": user_obj})
            if user_obj.exists() and user_obj.first().check_password(password):
                user = UserLoginSerializer(user_obj)
                data_list = {}
                data_list.update(user.data)

                logger.debug("Here")

                return Response(
                    {"message": "Login Successfully", "data": data_list, "code": 200}
                )
            else:
                message = "Unable to login with given credentials"
                return Response({"message": message, "code": 500, "data": {}})
        else:
            message = "Invalid login details."
            return Response({"message": message, "code": 500, "data": {}})

    # def get_queryset(self):
    #     logger.debug("GET users", extra={"self": self})
    #     return User.objects.filter(username=username)
