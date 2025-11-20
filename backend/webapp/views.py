from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from webapp.serializers import CarOwnerRegistrationSerializer, DriverRegistrationSerializer, MechanicRegistrationSerializer

# Create your views here.

@api_view(['POSt'])
def driver_registration(request):
    if request.method=='POST':
        serializer =  DriverRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                driver = serializer.save()
                return Response({
                    'message': 'Driver registered successfully',
                    'driver_id': driver.id
                    'username':driver.username
                }, status=status.HTTP_201_CREATED)
            except Exception as e:
                return Response({
                    'error': str(e)
                }, status=status.HTTP_400_BAD_REQUEST)
        return Response('error': serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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


