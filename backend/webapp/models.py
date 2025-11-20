from datetime import timedelta
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from math import radians, sin, cos, sqrt, atan2
from django.contrib.auth.models import User
from django.utils.crypto import get_random_string
# Create your models here.

class Driver(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    licence_number = models.CharField(max_length=50, unique=True)
    vehicle = models.ForeignKey('Vehicle', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_driver')
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        if self.vehicle and self.vehicle.assigned_driver.exists() and self.vehicle.assigned_driver.first() != self:
            raise ValidationError('This vehicle is already assigned to another driver')
    
    def __str__(self):
        return self.username

class Mechanic(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    speciality = models.CharField(max_length=100)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    location = models.CharField(max_length=255)
    
    def __str__(self):
        return self.username

class CarOwner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, unique=True)
    address = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username

class Vehicle(models.Model):
    VEHICLE_TYPES = (
        ('car', 'Car'),
        ('truck', 'Truck'),
        ('motorcycle', 'Motorcycle'),
        ('van', 'Van'),
    )
    
    owner = models.ForeignKey(CarOwner, on_delete=models.CASCADE, related_name='vehicles')
    vehicle_number = models.CharField(max_length=20, unique=True)
    model = models.CharField(max_length=100)
    manufacturer = models.CharField(max_length=100)
    vehicle_type = models.CharField(max_length=20, choices=VEHICLE_TYPES, default='car')
    year_of_manufacture = models.IntegerField()
    current_odometer = models.IntegerField(default=0)
    image = models.ImageField(upload_to='vehicle_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def clean(self):
        current_year = timezone.now().year
        if self.year_of_manufacture < 1900 or self.year_of_manufacture > current_year + 1:
            raise ValidationError('Invalid year of manufacture')
    
    def __str__(self):
        return self.vehicle_number

class Trip(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('ongoing', 'Ongoing'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )

    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='trips')
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='trips')
    start_lat = models.FloatField(null=True, blank=True)
    start_lng = models.FloatField(null=True, blank=True)
    end_lat = models.FloatField(null=True, blank=True)
    end_lng = models.FloatField(null=True, blank=True)
    distance_km = models.FloatField(default=0.0)
    started_at = models.DateTimeField(null=True, blank=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    def clean(self):
        if self.started_at and self.ended_at and self.started_at > self.ended_at:
            raise ValidationError('End time cannot be before start time')
        
        if self.status == 'completed' and not (self.end_lat and self.end_lng):
            raise ValidationError('Completed trips must have end coordinates')

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

    def start_trip(self, start_lat, start_lng):
        self.start_lat = start_lat
        self.start_lng = start_lng
        self.started_at = timezone.now()
        self.status = 'ongoing'
        self.save()

    def end_trip(self, end_lat, end_lng):
        self.end_lat = end_lat
        self.end_lng = end_lng
        self.ended_at = timezone.now()
        self.distance_km = self.calculate_distance()
        self.status = 'completed'
        self.save()

    def __str__(self):
        return f"Trip #{self.id} - {self.driver.username}"

class TripLocation(models.Model):
    trip = models.ForeignKey(Trip, on_delete=models.CASCADE, related_name='locations')
    latitude = models.FloatField()
    longitude = models.FloatField()
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"Location for trip {self.trip.id}"

class FuelLog(models.Model):
    FUEL_TYPES = (
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid'),
    )
    
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='fuel_logs')
    date = models.DateField()
    fuel_type = models.CharField(max_length=50, choices=FUEL_TYPES)
    quantity_liters = models.FloatField()
    price_per_liter = models.FloatField()
    total_cost = models.FloatField(editable=False)
    odometer_reading = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        self.total_cost = self.quantity_liters * self.price_per_liter
        super().save(*args, **kwargs)

    def clean(self):
        if self.quantity_liters <= 0:
            raise ValidationError('Quantity must be positive')
        if self.price_per_liter <= 0:
            raise ValidationError('Price per liter must be positive')

    def __str__(self):
        return f"Fuel log for {self.vehicle.vehicle_number} on {self.date}"

class ServiceType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    recommended_interval_km = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.name

class MaintenanceLog(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='maintenance_logs')
    service_type = models.ForeignKey(ServiceType, on_delete=models.SET_NULL, null=True)
    odometer_reading = models.IntegerField()
    description = models.TextField(blank=True)
    date = models.DateTimeField(default=timezone.now)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey(CarOwner, on_delete=models.SET_NULL, null=True)
    mechanic = models.ForeignKey(Mechanic, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.vehicle} - {self.service_type} on {self.date.date()}"

class PartReplacement(models.Model):
    maintenance_log = models.ForeignKey(MaintenanceLog, on_delete=models.CASCADE, related_name='replaced_parts')
    part_name = models.CharField(max_length=150)
    brand = models.CharField(max_length=100, blank=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    next_replacement_date = models.DateField(null=True, blank=True)
    next_replacement_km = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f"{self.part_name} ({self.brand})"

class Insurance(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='insurances')
    provider = models.CharField(max_length=150)
    policy_number = models.CharField(max_length=100, unique=True)
    start_date = models.DateField()
    expiry_date = models.DateField()
    document = models.FileField(upload_to="documents/insurance/", blank=True, null=True)
    created_by = models.ForeignKey(CarOwner, on_delete=models.SET_NULL, null=True)

    def clean(self):
        if self.expiry_date <= self.start_date:
            raise ValidationError('Expiry date must be after start date')

    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    def __str__(self):
        return f"{self.vehicle} - {self.policy_number}"

class Inspection(models.Model):
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='inspections')
    certificate_number = models.CharField(max_length=120)
    inspection_date = models.DateField()
    expiry_date = models.DateField()
    document = models.FileField(upload_to="documents/inspection/", blank=True, null=True)
    created_by = models.ForeignKey(CarOwner, on_delete=models.SET_NULL, null=True)

    def clean(self):
        if self.expiry_date <= self.inspection_date:
            raise ValidationError('Expiry date must be after inspection date')

    def __str__(self):
        return f"{self.vehicle} Inspection"

class License(models.Model):
    LICENSE_TYPES = (
        ("DRIVER", "Driver License"),
        ("VEHICLE", "Vehicle License"),
        ("OTHER", "Other"),
    )

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='licenses')
    license_type = models.CharField(max_length=20, choices=LICENSE_TYPES)
    license_number = models.CharField(max_length=120)
    issue_date = models.DateField()
    expiry_date = models.DateField()
    document = models.FileField(upload_to="documents/licenses/", blank=True, null=True)
    created_by = models.ForeignKey(CarOwner, on_delete=models.SET_NULL, null=True)

    def clean(self):
        if self.expiry_date <= self.issue_date:
            raise ValidationError('Expiry date must be after issue date')

    def __str__(self):
        return f"{self.license_type} - {self.license_number}"

class Reminder(models.Model):
    REMINDER_TYPES = (
        ("INSURANCE", "Insurance"),
        ("INSPECTION", "Inspection"),
        ("LICENSE", "License"),
        ("MAINTENANCE", "Maintenance"),
    )

    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='reminders')
    reminder_type = models.CharField(max_length=20, choices=REMINDER_TYPES)
    related_id = models.PositiveIntegerField()
    message = models.CharField(max_length=255)
    reminder_date = models.DateTimeField()
    sent = models.BooleanField(default=False)
    acknowledged = models.BooleanField(default=False)

    class Meta:
        ordering = ['reminder_date']

    def __str__(self):
        return f"{self.vehicle} - {self.reminder_type} Reminder"


class BaseToken(models.Model):
    key = models.CharField(max_length=40, primary_key=True)
    created = models.DateTimeField(auto_now_add=True)
    expires = models.DateTimeField()

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        if not self.expires:
            self.expires = timezone.now() + timedelta(days=30)
        return super().save(*args, **kwargs)

    def generate_key(self):
        return get_random_string(40)

    def is_expired(self):
        return timezone.now() > self.expires

    def __str__(self):
        return self.key

class DriverToken(BaseToken):
    driver = models.ForeignKey('Driver', on_delete=models.CASCADE, related_name='tokens')

class CarOwnerToken(BaseToken):
    car_owner = models.ForeignKey('CarOwner', on_delete=models.CASCADE, related_name='tokens')

class MechanicToken(BaseToken):
    mechanic = models.ForeignKey('Mechanic', on_delete=models.CASCADE, related_name='tokens')    