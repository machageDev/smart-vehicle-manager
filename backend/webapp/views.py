from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from webapp.models import DriverToken, MechanicToken
from webapp.serializers import CarOwnerRegistrationSerializer, DriverLoginSerializer, DriverRegistrationSerializer, MechanicLoginSerializer, MechanicRegistrationSerializer

# Create your views here.

@api_view(['POST'])
def driver_registration(request):   
    if request.method == 'POST':
        serializer = DriverRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                driver = serializer.save()
                return Response({
                    'message': 'Driver registered successfully',
                    'driver_id': driver.id,
                    'username': driver.username
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def car_owner_registration(request):   
    if request.method == 'POST':
        serializer = CarOwnerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                car_owner = serializer.save()
                return Response({
                    'message': 'Car owner registered successfully',
                    'car_owner_id': car_owner.id,
                    'username': car_owner.username
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                   
                   
@api_view(['POST'])
def mechanic_registration(request):    
    if request.method == 'POST':
        serializer = MechanicRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                mechanic = serializer.save()
                return Response({
                    'message': 'Mechanic registered successfully',
                    'mechanic_id': mechanic.id,
                    'username': mechanic.username
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)        

@api_view(['POST'])
#@authentication_classes([CustomTokenAuthentication])
#@permission_classes([IsAuthenticated])
def driver_login(request):
   
    if request.method == 'POST':
        serializer = DriverLoginSerializer(data=request.data)
        if serializer.is_valid():
            driver = serializer.validated_data['driver']
            
            # Create or get token
            token, created = DriverToken.objects.get_or_create(driver=driver)
            
            return Response({
                'message': 'Login successful',
                'token': token.key,
                'driver': {
                    'id': driver.id,
                    'username': driver.username,
                    'email': driver.email,
                    'phone_number': driver.phone_number
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])

def mechanic_login(request):
    if request.method =='POST':
        serializer = MechanicLoginSerializer(data=request.data)
        if serializer.is_valid():
            mechanic = serializer.validated_data['mechanic']
                   
        # Create or get token
        token, created = MechanicToken.objetcs.get_or_create(mechanic=mechanic)
        return Response({
            'message':'login successful',
            'token':token.key,
            'mechanic':{
                ''
            }
        })
        
