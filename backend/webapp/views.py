from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from webapp.serializers import DriverRegistrationSerializer

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
    return Response( 'error': serializer.errors, status=status.HTTP_400_BAD_REQUEST)



                   
                   
        


