# serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Driver, Mechanic, CarOwner, Vehicle, Trip, TripLocation,
    FuelLog, ServiceType, MaintenanceLog, PartReplacement,
    Insurance, Inspection, License, Reminder
)
from django.utils import timezone
from math import radians, sin, cos, sqrt, atan2

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}

# Registration Serializers
class DriverRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(write_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Driver
        fields = ['user', 'password', 'username', 'email', 'phone_number', 
                 'licence_number', 'vehicle', 'is_available']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=user_data.get('username'),
            email=user_data.get('email'),
            password=password,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        driver = Driver.objects.create(user=user, **validated_data)
        return driver

class MechanicRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(write_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = Mechanic
        fields = ['user', 'password', 'username', 'email', 'phone_number', 
                 'speciality', 'location', 'is_available']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=user_data.get('username'),
            email=user_data.get('email'),
            password=password,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        mechanic = Mechanic.objects.create(user=user, **validated_data)
        return mechanic

class CarOwnerRegistrationSerializer(serializers.ModelSerializer):
    user = UserSerializer(write_only=True)
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = CarOwner
        fields = ['user', 'password', 'username', 'email', 'phone_number', 'address']
    
    def create(self, validated_data):
        user_data = validated_data.pop('user')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            username=user_data.get('username'),
            email=user_data.get('email'),
            password=password,
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        
        car_owner = CarOwner.objects.create(user=user, **validated_data)
        return car_owner

# Main Model Serializers
class DriverSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    vehicle_details = serializers.SerializerMethodField()
    
    class Meta:
        model = Driver
        fields = ['id', 'user', 'username', 'email', 'phone_number', 'licence_number',
                 'vehicle', 'vehicle_details', 'is_available', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_vehicle_details(self, obj):
        if obj.vehicle:
            return {
                'id': obj.vehicle.id,
                'vehicle_number': obj.vehicle.vehicle_number,
                'model': obj.vehicle.model,
                'manufacturer': obj.vehicle.manufacturer
            }
        return None

class MechanicSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Mechanic
        fields = ['id', 'user', 'username', 'email', 'phone_number', 'speciality',
                 'location', 'is_available', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']


class MechanicLoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        email = data.get('email')
        password = data.get('password')
        
        try:
            mechanic = Mechanic.objects.get(email=email)
        except Mechanic.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No mechanic found with this email address'
            })
        
        if not mechanic.check_password(password):
            raise serializers.ValidationError({
                'password': 'Invalid password'
            })
        
        data['mechanic'] = mechanic
        return data
class DriverLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        try:
            driver = Driver.objects.get(username=username)
        except Driver.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No driver found with this email address'
            })
        
        if not driver.check_password(password):
            raise serializers.ValidationError({
                'password': 'Invalid password'
            })
        
        data['driver'] = driver
        return data
    
class CarOwnerLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        username = data.get('username')
        password = data.get('password')
        
        try:
            car_owner = CarOwner.objects.get(email=username)
        except CarOwner.DoesNotExist:
            raise serializers.ValidationError({
                'email': 'No car owner found with this email address'
            })
        
        if not car_owner.check_password(password):
            raise serializers.ValidationError({
                'password': 'Invalid password'
            })
        
        data['car_owner'] = car_owner
        return data  
      
class CarOwnerSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    vehicles_count = serializers.SerializerMethodField()
    
    class Meta:
        model = CarOwner
        fields = ['id', 'user', 'username', 'email', 'phone_number', 'address',
                 'vehicles_count', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_vehicles_count(self, obj):
        return obj.vehicles.count()

class VehicleListSerializer(serializers.ModelSerializer):
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    assigned_driver = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_number', 'model', 'manufacturer', 'vehicle_type',
                 'year_of_manufacture', 'owner', 'owner_name', 'assigned_driver',
                 'current_odometer', 'image', 'created_at']
    
    def get_assigned_driver(self, obj):
        driver = obj.assigned_driver.first()
        if driver:
            return {
                'id': driver.id,
                'username': driver.username,
                'phone_number': driver.phone_number
            }
        return None

class VehicleDetailSerializer(serializers.ModelSerializer):
    owner_details = CarOwnerSerializer(source='owner', read_only=True)
    assigned_driver = DriverSerializer(read_only=True)
    maintenance_logs_count = serializers.SerializerMethodField()
    fuel_logs_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Vehicle
        fields = ['id', 'vehicle_number', 'model', 'manufacturer', 'vehicle_type',
                 'year_of_manufacture', 'current_odometer', 'image',
                 'owner', 'owner_details', 'assigned_driver',
                 'maintenance_logs_count', 'fuel_logs_count',
                 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def get_maintenance_logs_count(self, obj):
        return obj.maintenance_logs.count()
    
    def get_fuel_logs_count(self, obj):
        return obj.fuel_logs.count()

class TripLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripLocation
        fields = ['id', 'latitude', 'longitude', 'timestamp']
        read_only_fields = ['timestamp']

class TripListSerializer(serializers.ModelSerializer):
    driver_name = serializers.CharField(source='driver.username', read_only=True)
    vehicle_number = serializers.CharField(source='vehicle.vehicle_number', read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Trip
        fields = ['id', 'driver', 'driver_name', 'vehicle', 'vehicle_number',
                 'status', 'distance_km', 'started_at', 'ended_at', 'duration']
    
    def get_duration(self, obj):
        if obj.started_at and obj.ended_at:
            duration = obj.ended_at - obj.started_at
            return str(duration)
        return None

class TripDetailSerializer(serializers.ModelSerializer):
    driver_details = DriverSerializer(source='driver', read_only=True)
    vehicle_details = VehicleListSerializer(source='vehicle', read_only=True)
    locations = TripLocationSerializer(many=True, read_only=True)
    duration = serializers.SerializerMethodField()
    
    class Meta:
        model = Trip
        fields = ['id', 'driver', 'driver_details', 'vehicle', 'vehicle_details',
                 'start_lat', 'start_lng', 'end_lat', 'end_lng', 'distance_km',
                 'started_at', 'ended_at', 'status', 'duration', 'locations']
        read_only_fields = ['distance_km', 'started_at', 'ended_at']
    
    def get_duration(self, obj):
        if obj.started_at and obj.ended_at:
            duration = obj.ended_at - obj.started_at
            return str(duration)
        return None

class TripCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Trip
        fields = ['driver', 'vehicle', 'start_lat', 'start_lng']
    
    def validate(self, data):
        driver = data.get('driver')
        vehicle = data.get('vehicle')
        
        if driver.vehicle != vehicle:
            raise serializers.ValidationError(
                "Driver is not assigned to this vehicle"
            )
        
        if not driver.is_available:
            raise serializers.ValidationError(
                "Driver is not available"
            )
        
        # Check if driver has ongoing trip
        ongoing_trip = Trip.objects.filter(
            driver=driver, 
            status__in=['pending', 'ongoing']
        ).exists()
        
        if ongoing_trip:
            raise serializers.ValidationError(
                "Driver already has an ongoing trip"
            )
        
        return data

class FuelLogSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source='vehicle.vehicle_number', read_only=True)
    cost_per_liter = serializers.FloatField(source='price_per_liter', read_only=True)
    
    class Meta:
        model = FuelLog
        fields = ['id', 'vehicle', 'vehicle_number', 'date', 'fuel_type',
                 'quantity_liters', 'cost_per_liter', 'total_cost', 
                 'odometer_reading', 'created_at']
        read_only_fields = ['total_cost', 'created_at']
    
    def validate_odometer_reading(self, value):
        vehicle = self.instance.vehicle if self.instance else self.initial_data.get('vehicle')
        if vehicle and value < vehicle.current_odometer:
            raise serializers.ValidationError(
                "Odometer reading cannot be less than current vehicle odometer"
            )
        return value

class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType
        fields = ['id', 'name', 'description', 'recommended_interval_km']

class PartReplacementSerializer(serializers.ModelSerializer):
    class Meta:
        model = PartReplacement
        fields = ['id', 'part_name', 'brand', 'cost', 
                 'next_replacement_date', 'next_replacement_km']

class MaintenanceLogListSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source='vehicle.vehicle_number', read_only=True)
    service_type_name = serializers.CharField(source='service_type.name', read_only=True)
    mechanic_name = serializers.CharField(source='mechanic.username', read_only=True, allow_null=True)
    
    class Meta:
        model = MaintenanceLog
        fields = ['id', 'vehicle', 'vehicle_number', 'service_type', 'service_type_name',
                 'odometer_reading', 'date', 'total_cost', 'mechanic', 'mechanic_name']

class MaintenanceLogDetailSerializer(serializers.ModelSerializer):
    vehicle_details = VehicleListSerializer(source='vehicle', read_only=True)
    service_type_details = ServiceTypeSerializer(source='service_type', read_only=True)
    mechanic_details = MechanicSerializer(source='mechanic', read_only=True)
    replaced_parts = PartReplacementSerializer(many=True, read_only=True)
    
    class Meta:
        model = MaintenanceLog
        fields = ['id', 'vehicle', 'vehicle_details', 'service_type', 'service_type_details',
                 'odometer_reading', 'description', 'date', 'total_cost',
                 'created_by', 'mechanic', 'mechanic_details', 'replaced_parts']

class MaintenanceLogCreateSerializer(serializers.ModelSerializer):
    replaced_parts = PartReplacementSerializer(many=True, required=False)
    
    class Meta:
        model = MaintenanceLog
        fields = ['id', 'vehicle', 'service_type', 'odometer_reading',
                 'description', 'total_cost', 'mechanic', 'replaced_parts']
    
    def create(self, validated_data):
        parts_data = validated_data.pop('replaced_parts', [])
        maintenance_log = MaintenanceLog.objects.create(**validated_data)
        
        for part_data in parts_data:
            PartReplacement.objects.create(maintenance_log=maintenance_log, **part_data)
        
        # Update vehicle odometer if this reading is higher
        vehicle = maintenance_log.vehicle
        if maintenance_log.odometer_reading > vehicle.current_odometer:
            vehicle.current_odometer = maintenance_log.odometer_reading
            vehicle.save()
        
        return maintenance_log

class InsuranceSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source='vehicle.vehicle_number', read_only=True)
    is_expired = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = Insurance
        fields = ['id', 'vehicle', 'vehicle_number', 'provider', 'policy_number',
                 'start_date', 'expiry_date', 'document', 'is_expired', 
                 'days_until_expiry', 'created_by']
        read_only_fields = ['created_by']
    
    def get_is_expired(self, obj):
        return obj.is_expired()
    
    def get_days_until_expiry(self, obj):
        today = timezone.now().date()
        if obj.expiry_date > today:
            return (obj.expiry_date - today).days
        return 0

class InspectionSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source='vehicle.vehicle_number', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = Inspection
        fields = ['id', 'vehicle', 'vehicle_number', 'certificate_number',
                 'inspection_date', 'expiry_date', 'document', 'is_expired']
    
    def get_is_expired(self, obj):
        return obj.expiry_date < timezone.now().date()

class LicenseSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source='vehicle.vehicle_number', read_only=True)
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = License
        fields = ['id', 'vehicle', 'vehicle_number', 'license_type', 'license_number',
                 'issue_date', 'expiry_date', 'document', 'is_expired']
    
    def get_is_expired(self, obj):
        return obj.expiry_date < timezone.now().date()

class ReminderSerializer(serializers.ModelSerializer):
    vehicle_number = serializers.CharField(source='vehicle.vehicle_number', read_only=True)
    is_overdue = serializers.SerializerMethodField()
    
    class Meta:
        model = Reminder
        fields = ['id', 'vehicle', 'vehicle_number', 'reminder_type', 'related_id',
                 'message', 'reminder_date', 'sent', 'acknowledged', 'is_overdue']
        read_only_fields = ['sent']
    
    def get_is_overdue(self, obj):
        return obj.reminder_date < timezone.now()

# Dashboard Statistics Serializers
class VehicleStatsSerializer(serializers.Serializer):
    total_vehicles = serializers.IntegerField()
    active_vehicles = serializers.IntegerField()
    vehicles_needing_maintenance = serializers.IntegerField()
    total_distance_km = serializers.FloatField()

class DriverStatsSerializer(serializers.Serializer):
    total_drivers = serializers.IntegerField()
    available_drivers = serializers.IntegerField()
    active_trips = serializers.IntegerField()

class MaintenanceStatsSerializer(serializers.Serializer):
    total_maintenance_logs = serializers.IntegerField()
    pending_maintenance = serializers.IntegerField()
    total_maintenance_cost = serializers.DecimalField(max_digits=10, decimal_places=2)

# File Upload Serializers
class DocumentUploadSerializer(serializers.Serializer):
    document = serializers.FileField()
    
    def validate_document(self, value):
        valid_extensions = ['.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx']
        file_extension = value.name.split('.')[-1].lower()
        
        if f'.{file_extension}' not in valid_extensions:
            raise serializers.ValidationError(
                f'Unsupported file format. Supported formats: {", ".join(valid_extensions)}'
            )
        
        # Limit file size to 10MB
        if value.size > 10 * 1024 * 1024:
            raise serializers.ValidationError('File size cannot exceed 10MB')
        
        return value

# Location-based Serializers
class NearbyMechanicSerializer(serializers.Serializer):
    mechanic_id = serializers.IntegerField()
    username = serializers.CharField()
    speciality = serializers.CharField()
    distance_km = serializers.FloatField()
    location = serializers.CharField()

class TripStartSerializer(serializers.Serializer):
    start_lat = serializers.FloatField(required=True)
    start_lng = serializers.FloatField(required=True)
    
    def validate_start_lat(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError('Latitude must be between -90 and 90')
        return value
    
    def validate_start_lng(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError('Longitude must be between -180 and 180')
        return value

class TripEndSerializer(serializers.Serializer):
    end_lat = serializers.FloatField(required=True)
    end_lng = serializers.FloatField(required=True)
    
    def validate_end_lat(self, value):
        if not (-90 <= value <= 90):
            raise serializers.ValidationError('Latitude must be between -90 and 90')
        return value
    
    def validate_end_lng(self, value):
        if not (-180 <= value <= 180):
            raise serializers.ValidationError('Longitude must be between -180 and 180')
        return value