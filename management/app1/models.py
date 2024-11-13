from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Supervisor Model
class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

# Manager Model
class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254)
    mobile_number = models.CharField(max_length=15)

    def __str__(self):
        return self.name

# Worker Model
class Worker(models.Model):
    name = models.CharField(max_length=100)
    adhar_no = models.CharField(max_length=12, default='000000000000')  # Default value for adhar_no
    is_working = models.BooleanField(default=False)

    def __str__(self):
        return self.name


# Project Model
class Project(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    budget = models.DecimalField(max_digits=10, decimal_places=2)
    timeline = models.DateField()
    supervisor = models.ForeignKey(Supervisor, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

# Task Model
class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    start_date = models.DateField(null=True, blank=True)  # Allowing null for start_date
    end_date = models.DateField(null=True, blank=True)    # Allowing null for end_date
    project = models.ForeignKey('Project', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='task_images/', null=True, blank=True)
    workers = models.ManyToManyField('Worker', blank=True)
    resources = models.ManyToManyField('Resource', blank=True)
    def __str__(self):
        return self.title

class Resource(models.Model):
    MATERIAL_CHOICES = [
        ('cement', 'Cement'),
        ('sand', 'Sand'),
        ('bricks', 'Bricks'),
        ('gravel', 'Gravel'),
        ('steel', 'Steel'),
        ('concrete', 'Concrete'),
    ]
    material_type = models.CharField(max_length=10, choices=MATERIAL_CHOICES, default='cement')  # Set default value
    total_quantity = models.IntegerField(default=0)  # Set default value for total_quantity
    quantity_used = models.IntegerField(default=0)   # Quantity used
    quantity_left = models.IntegerField(default=0)   # Remaining quantity
    arrival_date = models.DateField()  # Date when material arrived
    project = models.ForeignKey('Project', on_delete=models.CASCADE)  # Link to a project

    def save(self, *args, **kwargs):
        """Automatically update `quantity_left` when saving the resource."""
        self.quantity_left = self.total_quantity - self.quantity_used
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_material_type_display()} - Total: {self.total_quantity}, Used: {self.quantity_used}, Left: {self.quantity_left}"
