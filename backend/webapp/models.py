from django.db import models

# Create your models here.

class Driver(models.Model):
    username=models.CharFiield(max_length=255,unique=True)
    email=models.EmailField(unique=True)
    phone_number=models.CharField(max_length=15,unique=True)
    licence_number=models.CharField(max_length=50,unique=True)
    vehicle_number=models.CharField(max_length=20,unique=True)
    is_available=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.username
    
    
class Mechanic(models.Model):
    username=models.CharField(max_length=255,unique=True)
    email=models.EmailField(unique=True)
    phone_number=models.CharField(max_length=15,unique=True)
    speciality=models.CharField(max_length=100)
    is_available=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255)
    def __str__(self):
        return self.username    
    
    
class Carowner(models.Model):
    username=models.CharField(max_length=255,unique=True)
    email=models.EmailField(unique=True)
    phone_number=models.CharField(max_length=15,unique=True)
    address=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)  
    def __str__(self):
            return self.username
      