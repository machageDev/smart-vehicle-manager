
from rest_framework import permissions
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import DriverToken, CarOwnerToken, MechanicToken


class IsAuthenticated(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return bool(request.user and getattr(request.user, 'is_authenticated', False))


class DriverTokenAuthentication(BaseAuthentication):
    
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(f" RAW Auth header: {auth_header}")

        if not auth_header or not auth_header.startswith('Bearer '):
            print(" No Bearer token found")
            return None

        try:
            # Extract token
            token_key = auth_header.split(' ')[1].strip()
            print(f" Looking for driver token: '{token_key}'")

            # Find the driver token
            driver_token = DriverToken.objects.get(key=token_key)
            driver = driver_token.driver

            print(f"  SUCCESS: Authenticated driver {driver.username} (ID: {driver.id})")

            # Add required attributes for DRF
            driver.is_authenticated = True
            driver.is_anonymous = False

            return (driver, driver_token)

        except DriverToken.DoesNotExist:
            print(f"  Driver token not found: {token_key}")
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            print(f"  Driver authentication error: {e}")
            raise AuthenticationFailed('Authentication failed')

    def authenticate_header(self, request):
        return 'Bearer'


class CarOwnerTokenAuthentication(BaseAuthentication):
   
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(f" RAW Auth header: {auth_header}")

        if not auth_header or not auth_header.startswith('Bearer '):
            print(" No Bearer token found")
            return None

        try:
            # Extract token
            token_key = auth_header.split(' ')[1].strip()
            print(f" Looking for car owner token: '{token_key}'")

            # Find the car owner token
            car_owner_token = CarOwnerToken.objects.get(key=token_key)
            car_owner = car_owner_token.car_owner

            print(f"  SUCCESS: Authenticated car owner {car_owner.username} (ID: {car_owner.id})")

            # Add required attributes for DRF
            car_owner.is_authenticated = True
            car_owner.is_anonymous = False

            return (car_owner, car_owner_token)

        except CarOwnerToken.DoesNotExist:
            print(f"  Car owner token not found: {token_key}")
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            print(f"  Car owner authentication error: {e}")
            raise AuthenticationFailed('Authentication failed')

    def authenticate_header(self, request):
        return 'Bearer'


class MechanicTokenAuthentication(BaseAuthentication):
   
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(f" RAW Auth header: {auth_header}")

        if not auth_header or not auth_header.startswith('Bearer '):
            print(" No Bearer token found")
            return None

        try:
            # Extract token
            token_key = auth_header.split(' ')[1].strip()
            print(f" Looking for mechanic token: '{token_key}'")

            # Find the mechanic token
            mechanic_token = MechanicToken.objects.get(key=token_key)
            mechanic = mechanic_token.mechanic

            print(f"  SUCCESS: Authenticated mechanic {mechanic.username} (ID: {mechanic.id})")

            # Add required attributes for DRF
            mechanic.is_authenticated = True
            mechanic.is_anonymous = False

            return (mechanic, mechanic_token)

        except MechanicToken.DoesNotExist:
            print(f"  Mechanic token not found: {token_key}")
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            print(f"  Mechanic authentication error: {e}")
            raise AuthenticationFailed('Authentication failed')

    def authenticate_header(self, request):
        return 'Bearer'


# Combined authentication class that tries all user types
class MultiUserTokenAuthentication(BaseAuthentication):
   
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        print(f" RAW Auth header: {auth_header}")

        if not auth_header or not auth_header.startswith('Bearer '):
            print(" No Bearer token found")
            return None

        token_key = auth_header.split(' ')[1].strip()
        print(f" Looking for token in all user types: '{token_key}'")

        # Try Driver token first
        try:
            driver_token = DriverToken.objects.get(key=token_key)
            driver = driver_token.driver
            print(f"  SUCCESS: Authenticated driver {driver.username} (ID: {driver.id})")
            driver.is_authenticated = True
            driver.is_anonymous = False
            return (driver, driver_token)
        except DriverToken.DoesNotExist:
            print(" Token not found in Driver tokens")

        # Try CarOwner token
        try:
            car_owner_token = CarOwnerToken.objects.get(key=token_key)
            car_owner = car_owner_token.car_owner
            print(f"  SUCCESS: Authenticated car owner {car_owner.username} (ID: {car_owner.id})")
            car_owner.is_authenticated = True
            car_owner.is_anonymous = False
            return (car_owner, car_owner_token)
        except CarOwnerToken.DoesNotExist:
            print(" Token not found in CarOwner tokens")

        # Try Mechanic token
        try:
            mechanic_token = MechanicToken.objects.get(key=token_key)
            mechanic = mechanic_token.mechanic
            print(f"  SUCCESS: Authenticated mechanic {mechanic.username} (ID: {mechanic.id})")
            mechanic.is_authenticated = True
            mechanic.is_anonymous = False
            return (mechanic, mechanic_token)
        except MechanicToken.DoesNotExist:
            print(" Token not found in Mechanic tokens")

        print(f"  Token not found in any user type: {token_key}")
        raise AuthenticationFailed('Invalid token')

    def authenticate_header(self, request):
        return 'Bearer'


# Permission classes for specific user types
class IsDriver(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return bool(request.user and 
                   getattr(request.user, 'is_authenticated', False) and 
                   hasattr(request.user, 'driver_ptr'))


class IsCarOwner(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return bool(request.user and 
                   getattr(request.user, 'is_authenticated', False) and 
                   hasattr(request.user, 'carowner_ptr'))


class IsMechanic(permissions.BasePermission):
    
    def has_permission(self, request, view):
        return bool(request.user and 
                   getattr(request.user, 'is_authenticated', False) and 
                   hasattr(request.user, 'mechanic_ptr'))


class IsDriverOrCarOwner(permissions.BasePermission):
    
    def has_permission(self, request, view):
        if not request.user or not getattr(request.user, 'is_authenticated', False):
            return False
        
        return hasattr(request.user, 'driver_ptr') or hasattr(request.user, 'carowner_ptr')