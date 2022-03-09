from django.contrib.auth.models import User, Group
from rest_framework import serializers
from scheduler.models import Date, Note


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']

class NoteSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = Note
        fields = ['id', 'user', 'message']

class DateSerializer(serializers.ModelSerializer):
    notes = NoteSerializer(many=True, read_only=True)
    users = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Date
        fields = ['date', 'users', 'notes']
        lookup_field = 'date'