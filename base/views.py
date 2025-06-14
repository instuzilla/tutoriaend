
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from .utils import calculate_distance
from copy  import deepcopy
from .models import TeacherProfile
from .serializer import TeacherProfileSerializer

@api_view(['GET'])
@permission_classes([AllowAny])
def home(request):
    """
    Home view that returns a simple welcome message.
    """
    return Response({"message": "Welcome to the Tutoria API!"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def protected_view(request):
    """
    A protected view that requires authentication.
    """
    return Response({"detail": f"This is a protected view, accessed by {request.user.first_name} {request.user.last_name}!"})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_location(request):
    """
    A protected view to set the user's location.
    Expects a JSON body with a 'location' field.
    """
    print("initiated set_location view")
    location = request.data.get('location')
    if not location:
        return Response({"error": "Location is required."}, status=400)
    # Check if user already has a location
    previous_location = getattr(request.user, "location", None)
    update_param = request.data.get("update", False)

    
    if previous_location:
        distance = calculate_distance(previous_location, location)
        print(f"Previous location: {previous_location}, New location: {location}, Distance: {distance} km")
        if distance is not None and distance >= .2 and not update_param:
            return Response(
                {
                    "detail": "Location update available. The new location is more than 200 meters away from the previous location.",
                    "distance_km": round(distance, 3),
                    "update_required": True
                },
                status=200
            )
        else:
            return Response({"detail": "Location don't need to be updated. The new location is within 200 meters of the previous location."},status=200)
    user = request.user
    user.location = location
    user.save()
    return Response({"detail": "Location updated successfully."}, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_teacher(request):
    teacher = TeacherProfile.objects.filter(user=request.user)
    if not teacher.exists():
        data = deepcopy(request.data)
        data['user'] = request.user.id
        print(data)
        serializer = TeacherProfileSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            request.user.is_teacher = True
            request.user.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    else:
        return Response({"detail": "Teacher profile already exists."}, status=status.HTTP_400_BAD_REQUEST)
   
    




