from rest_framework import serializers
from .models import Supervisor, Manager, Project, Worker, Task
from django.contrib.auth.models import User
from .models import User, Manager, Supervisor, Worker, Task,Resource

class UserSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=[('manager', 'Manager'), ('supervisor', 'Supervisor')])
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
    mobile_number = serializers.CharField(max_length=15)
 
    class Meta:
        model = User
        fields = ['username', 'password', 'role', 'name', 'email', 'mobile_number']
        extra_kwargs = {'password': {'write_only': True}}
 
    def create(self, validated_data):
        role = validated_data.pop('role')
        name = validated_data.pop('name')
        email = validated_data.pop('email')
        mobile_number = validated_data.pop('mobile_number')
 
        user = User(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
 
        if role == 'manager':
            Manager.objects.create(user=user, name=name, email=email, mobile_number=mobile_number)
        elif role == 'supervisor':
            Supervisor.objects.create(user=user, name=name, email=email, mobile_number=mobile_number)
 
        return user
 
class SupervisorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supervisor
        fields = ['id', 'user', 'name', 'email', 'mobile_number']
 
class ManagerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Manager
        fields = ['id', 'user', 'name', 'email', 'mobile_number']
 
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ['id', 'name', 'location', 'budget', 'timeline', 'supervisor']
        extra_kwargs = {'created_by': {'read_only': True}}  # Ensure created_by is read-only

class WorkerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Worker
        fields = ['id', 'name', 'adhar_no', 'is_working']

    def validate(self, data):
        # If the worker is already working (is_working is True), they cannot be assigned to another task
        if data['is_working'] == True:
            raise serializers.ValidationError("Worker is already assigned to a task and is currently working.")
        return data
    
class ResourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Resource
        fields = ['id', 'material_type', 'total_quantity', 'quantity_used', 'quantity_left', 'arrival_date', 'project']



class TaskSerializer(serializers.ModelSerializer):
    workers = serializers.ListField(child=serializers.CharField(), write_only=True)  # For assigning workers by adhar_no
    resources = serializers.ListField(child=serializers.IntegerField(), write_only=True)  # List of resource IDs

    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'start_date', 'end_date', 'project', 'image', 'workers', 'resources']

    def create(self, validated_data):
        workers_data = validated_data.pop('workers', [])
        resources_data = validated_data.pop('resources', [])
        task = Task.objects.create(**validated_data)

        # Assign workers to task
        for adhar_no in workers_data:
            try:
                worker = Worker.objects.get(adhar_no=adhar_no)
                if not worker.is_working:
                    task.workers.add(worker)
                    worker.is_working = True
                    worker.save()
                else:
                    raise serializers.ValidationError(f"Worker with Adhar No {adhar_no} is already working.")
            except Worker.DoesNotExist:
                raise serializers.ValidationError(f"Worker with Adhar No {adhar_no} does not exist.")

        
            return task