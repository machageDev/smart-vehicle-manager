from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from webapp.authentication import CarOwnerTokenAuthentication, DriverTokenAuthentication, MechanicTokenAuthentication
from webapp.models import CarOwnerToken, DriverToken, MechanicToken
from webapp.permissions import IsAuthenticated
from webapp.serializers import CarOwnerLoginSerializer, CarOwnerProfileSerializer, CarOwnerRegistrationSerializer, ChangePasswordSerializer, DriverLoginSerializer, DriverProfileSerializer, DriverRegistrationSerializer, MechanicLoginSerializer, MechanicProfileSerializer, MechanicRegistrationSerializer

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
def car_owner_login(request):
    
    if request.method == 'POST':
        serializer = CarOwnerLoginSerializer(data=request.data)
        if serializer.is_valid():
            car_owner = serializer.validated_data['car_owner']
            
            # Create or get token
            token, created = CarOwnerToken.objects.get_or_create(car_owner=car_owner)
            
            return Response({
                'message': 'Login successful',
                'token': token.key,
                'car_owner': {
                    'id': car_owner.id,
                    'username': car_owner.username,
                    'email': car_owner.email,
                    'phone_number': car_owner.phone_number
                }
            }, status=status.HTTP_200_OK)
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
                 'id': mechanic.id,
                    'username': mechanic.username,
                    'email': mechanic.email,
                    'phone_number': mechanic.phone_number,
                    'speciality': mechanic.speciality
                }
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
@api_view(['POST'])
@authentication_classes([DriverTokenAuthentication])
@permission_classes([IsAuthenticated])
def driver_logout(request):
    
    try:
        # Get the token from the request
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_key = auth_header.split(' ')[1]
        
       
        DriverToken.objects.filter(key=token_key).delete()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([CarOwnerTokenAuthentication])
@permission_classes([IsAuthenticated])
def car_owner_logout(request):
    
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_key = auth_header.split(' ')[1]
        
        CarOwnerToken.objects.filter(key=token_key).delete()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([MechanicTokenAuthentication])
@permission_classes([IsAuthenticated])
def mechanic_logout(request):
  
    try:
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token_key = auth_header.split(' ')[1]
        
        MechanicToken.objects.filter(key=token_key).delete()
        
        return Response({
            'message': 'Logout successful'
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': 'Logout failed'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([DriverTokenAuthentication])
@permission_classes([IsAuthenticated])
def driver_change_password(request):
   
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([CarOwnerTokenAuthentication])
@permission_classes([IsAuthenticated])
def car_owner_change_password(request):
    
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@authentication_classes([MechanicTokenAuthentication])
@permission_classes([IsAuthenticated])
def mechanic_change_password(request):
    
    serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({
            'message': 'Password changed successfully'
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'PUT'])
@authentication_classes([DriverTokenAuthentication])
@permission_classes([IsAuthenticated])
def driver_profile(request):
    
    if request.method == 'GET':
        serializer = DriverProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = DriverProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'driver': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@authentication_classes([CarOwnerTokenAuthentication])
@permission_classes([IsAuthenticated])
def car_owner_profile(request):
    
    if request.method == 'GET':
        serializer = CarOwnerProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = CarOwnerProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'car_owner': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT'])
@authentication_classes([MechanicTokenAuthentication])
@permission_classes([IsAuthenticated])
def mechanic_profile(request):
    
    if request.method == 'GET':
        serializer = MechanicProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    elif request.method == 'PUT':
        serializer = MechanicProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated successfully',
                'mechanic': serializer.data
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)