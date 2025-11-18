from django.db import models
from django.utils import timezone
from math import radians, sin, cos, sqrt, atan2
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
        
class Vehicle(models.Model):
    owner=models.ForeignKey(Carowner,on_delete=models.CASCADE)
    vehicle_number=models.CharField(max_length=20,unique=True)
    model=models.CharField(max_length=100)
    manufacturer=models.CharField(max_length=100)
    year_of_manufacture=models.IntegerField()
    image=models.ImageField(upload_to='vehicle_images/',null=True,blank=True)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return self.vehicle_number      


class Trip(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
    )

    user = models.ForeignKey(Driver, on_delete=models.CASCADE)
    start_lat = models.FloatField(null=True, blank=True)
    start_lng = models.FloatField(null=True, blank=True)
    end_lat = models.FloatField(null=True, blank=True)
    end_lng = models.FloatField(null=True, blank=True)

    distance_km = models.FloatField(default=0.0)

    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def __str__(self):
        return f"Trip #{self.id} - {self.user.username}"

    # --- DISTANCE CALCULATION (Haversine formula) ---
    def calculate_distance(self):
        if self.start_lat and self.end_lat:
            R = 6371  # Earth radius in KM

            lat1 = radians(self.start_lat)
            lon1 = radians(self.start_lng)
            lat2 = radians(self.end_lat)
            lon2 = radians(self.end_lng)

            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
            c = 2 * atan2(sqrt(a), sqrt(1 - a))

            return round(R * c, 2)
        return 0.0

    def end_trip(self, end_lat, end_lng):
        self.end_lat = end_lat
        self.end_lng = end_lng
        self.ended_at = timezone.now()
        self.distance_km = self.calculate_distance()
        self.status = 'completed'
        self.save()


class TripLocation(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='locations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Location for trip {self.trip.id}"


class Fuellog(models.Model):
    vehicle=models.ForeignKey(Vehicle,on_delete=models.CASCADE)
    date=models.DateField()
    fuel_type=models.CharField(max_length=50)
    quantity_liters=models.FloatField()
    price_per_liter=models.FloatField()
    total_cost=models.FloatField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Fuel log for {self.vehicle.vehicle_number} on {self.date}"
    
    
class ServiceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name


class MaintenanceLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE)
    service_type = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True)
    odometer_reading = models.IntegerField()
    description = models.TextField(blank=True)
    date = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(Driver, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.vehicle} - {self.service_type} on {self.date.date()}"    

class PartReplacement(models.Model):
    maintenance_log = models.ForeignKey(MaintenanceLog, on_delete=models.CASCADE, related_name='replaced_parts')
    part_name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    next_replacement_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.part_name} ({self.brand})"
        