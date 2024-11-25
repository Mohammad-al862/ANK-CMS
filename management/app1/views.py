from django.shortcuts import render
from django.http import JsonResponse
from rest_framework import permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .models import Manager, Supervisor, Project, Task, Worker,Resource
from .serializers import UserSerializer, ProjectSerializer, TaskSerializer, WorkerSerializer, SupervisorSerializer, ManagerSerializer,ResourceSerializer
from django.contrib.auth import authenticate, login, logout
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth import get_user_model
from rest_framework import serializers, status
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings



@api_view(['POST'])
def register(request):
    """Register a new Manager or Supervisor."""
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({'message': 'User created', 'token': token.key}, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['POST'])
def login_view(request):
    """Login a user."""
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({'message': 'Login successful', 'token': token.key})
    return Response({'message': 'Invalid credentials'}, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Logout a user."""
    logout(request)
    return Response({'message': 'Logout successful'})
 
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def password_reset_request(request):
    """Request a password reset token (Managers and Supervisors only)."""
    if not hasattr(request.user, 'manager') and not hasattr(request.user, 'supervisor'):
        return Response({'message': 'You do not have permission to reset password.'}, status=status.HTTP_403_FORBIDDEN)
    
    user = request.user
    
    # Generate a token for password reset
    token = default_token_generator.make_token(user)
    
    # Return the token directly in the response
    return Response({'message': 'Password reset token generated successfully.', 'reset_token': token}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reset_password(request, username, token):
    """Reset password with new password (Managers and Supervisors only)."""
    try:
        user = get_user_model().objects.get(username=username)
    except get_user_model().DoesNotExist:
        return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Validate token
    if not default_token_generator.check_token(user, token):
        return Response({'message': 'Invalid token or token expired'}, status=status.HTTP_400_BAD_REQUEST)

    # Check if the user is manager or supervisor
    if not hasattr(user, 'manager') and not hasattr(user, 'supervisor'):
        return Response({'message': 'You do not have permission to reset password.'}, status=status.HTTP_403_FORBIDDEN)
    
    new_password = request.data.get('new_password')
    if not new_password:
        return Response({'message': 'New password is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Set the new password
    user.set_password(new_password)
    user.save()

    return Response({'message': 'Password reset successful'}, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def my_profile(request):
    """Get the logged-in user's profile details."""
    user_data = {
        "username": request.user.username,
        "email": request.user.email,  # Ensure user email is available
    }
 
    if hasattr(request.user, 'manager'):
        manager = request.user.manager
        serializer = ManagerSerializer(manager)
        return Response({**user_data, **serializer.data})  # Combine user and manager data
 
    elif hasattr(request.user, 'supervisor'):
        supervisor = request.user.supervisor
        serializer = SupervisorSerializer(supervisor)
        return Response({**user_data, **serializer.data})  # Combine user and supervisor data
 
    return Response({'message': 'Profile not found.'}, status=status.HTTP_404_NOT_FOUND)
 
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_project(request):
    """Create a new project (Managers only)."""
    if not hasattr(request.user, 'manager'):
        return Response({'message': 'You do not have permission to create a project.'}, status=status.HTTP_403_FORBIDDEN)
 
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_projects(request):
    """Get a list of projects (Managers only)."""
    if not hasattr(request.user, 'manager'):
        return Response({'message': 'You do not have permission to view projects.'}, status=status.HTTP_403_FORBIDDEN)
 
    projects = Project.objects.all()
    serializer = ProjectSerializer(projects, many=True)
    return Response(serializer.data)
 

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_task(request):
    """Create a new task (Supervisors only)."""
    if not hasattr(request.user, 'supervisor'):
        return Response({'message': 'You do not have permission to create a task.'}, status=status.HTTP_403_FORBIDDEN)
 
    serializer = TaskSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
 
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_tasks(request):
    """Get a list of tasks (All users can see tasks)."""
    tasks = Task.objects.all()
    serializer = TaskSerializer(tasks, many=True)
    return Response(serializer.data)
 
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def task_detail(request, pk):
    """Retrieve, update, or delete a task."""
    try:
        task = Task.objects.get(pk=pk)
    except Task.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
 
    if hasattr(request.user, 'supervisor'):
        if request.method == 'GET':
            serializer = TaskSerializer(task)
            return Response(serializer.data)
 
        elif request.method == 'PUT':
            serializer = TaskSerializer(task, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
        elif request.method == 'DELETE':
            task.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
 
    return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)
 
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def get_workers(request):
    """Get a list of workers (Supervisors only)."""
    if not hasattr(request.user, 'supervisor'):
        return Response({'message': 'You do not have permission to view workers.'}, status=status.HTTP_403_FORBIDDEN)
 
    workers = Worker.objects.all()
    serializer = WorkerSerializer(workers, many=True)
    return Response(serializer.data)
 
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def create_worker(request):
    """Create a new worker (Supervisors only)."""
    if not hasattr(request.user, 'supervisor'):
        return Response({'message': 'You do not have permission to create a worker.'}, status=status.HTTP_403_FORBIDDEN)
 
    serializer = WorkerSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([permissions.IsAuthenticated])
def worker_detail(request, pk):
    """Retrieve, update, or delete a worker."""
    try:
        worker = Worker.objects.get(pk=pk)
    except Worker.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
 
    if hasattr(request.user, 'supervisor'):
        # Supervisors can perform all actions
        if request.method == 'GET':
            serializer = WorkerSerializer(worker)
            return Response(serializer.data)
 
        elif request.method == 'PUT':
            serializer = WorkerSerializer(worker, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
        elif request.method == 'DELETE':
            worker.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
 
    return Response({'message': 'You do not have permission to perform this action.'}, status=status.HTTP_403_FORBIDDEN)

# Create a new resource (Managers only)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_resource(request):
    """Create a new resource (Managers only)."""
    if not hasattr(request.user, 'manager'):
        return Response({'message': 'You do not have permission to create a resource.'}, status=status.HTTP_403_FORBIDDEN)
    
    serializer = ResourceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# List all resources
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_resources(request):
    """Get a list of resources (Managers and Supervisors)."""
    resources = Resource.objects.all()
    serializer = ResourceSerializer(resources, many=True)
    return Response(serializer.data)

# Retrieve, update, or delete a specific resource
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def resource_detail(request, pk):
    """Retrieve, update, or delete a resource."""
    try:
        resource = Resource.objects.get(pk=pk)
    except Resource.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = ResourceSerializer(resource)
        return Response(serializer.data)

    elif request.method == 'PUT':
        serializer = ResourceSerializer(resource, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        resource.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
