from django.shortcuts import HttpResponse
from django.contrib.auth.models import User
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.parsers import JSONParser 
from scheduler.models import Date, Note
from scheduler.serializers import DateSerializer, NoteSerializer, UserSerializer

def index(request):
    return HttpResponse('Hello World')

class UserViewSet(viewsets.ModelViewSet):
    """
    Api Endpoint for users
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all()
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]


@api_view(['GET', 'PUT'])
def getDateById(request, id):
    try:
        date = Date.objects.get(date=id)
    except Date.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = DateSerializer(date, context={'request': request})
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = DateSerializer(date, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def saveDate(request):
    if request.method == 'POST':
        serializer = DateSerializer(data=request.data)
        if serializer.is_valid():
            newDate = serializer.save()
            return Response(newDate.id, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    
    
    