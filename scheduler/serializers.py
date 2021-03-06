from django.contrib.auth.models import User, Group
from rest_framework import serializers
from rest_framework.authentication import authenticate
from scheduler.models import Date, Note
import logging

logger = logging.getLogger(__name__)


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()

    class Meta:
        model = User
        fields = ["id", "username", "email"]


class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ["username", "password"]


class UserLoginSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150)

    class Meta:
        model = User
        fields = ("id", "username")

    def validate(self, data):
        username = data.get("username", None)
        password = data.get("password", None)
        if username and password:
            user = authenticate(username=username, password=password)
            if user:
                data["user"] = user
            data["user"] = user
        return data


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ["url", "name"]


class NoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    user_id = serializers.PrimaryKeyRelatedField(
        write_only=True, source="user", queryset=User.objects.all()
    )
    date = serializers.PrimaryKeyRelatedField(queryset=Date.objects.all())

    class Meta:
        model = Note
        fields = ["id", "date", "user", "user_id", "message"]


class DateSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)
    user_ids = serializers.PrimaryKeyRelatedField(
        write_only=True, many=True, source="users", queryset=User.objects.all()
    )
    notes = NoteSerializer(many=True)

    class Meta:
        model = Date
        fields = ["date", "users", "notes", "user_ids"]
        lookup_field = "date"

    def create(self, validated_data):
        notes_data = validated_data.pop("notes", [])
        users_data = validated_data.pop("users", [])

        date = Date.objects.create(**validated_data)
        date.users.set(users_data)

        for note_data in notes_data:
            Note.objects.create(date=date, **note_data)
        return date

    def update(self, instance, validated_data):
        # Note data not dealt with
        users_data = validated_data.pop("users", [])

        instance.users.set(users_data)
        instance.save()

        return instance


class DateMonthSerializer(serializers.ModelSerializer):
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Date
        fields = ["date", "users"]
        lookup_field = "date"
