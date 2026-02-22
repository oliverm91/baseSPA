from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.core.exceptions import PermissionDenied
from . import services, serializers

class ListingListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        listings = services.get_active_listings()
        serializer = serializers.ListingSerializer(listings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ListingCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = serializers.ListingSerializer(data=request.data)
        if serializer.is_valid():
            try:
                listing = services.create_listing(
                    seller=request.user,
                    title=serializer.validated_data['title'],
                    description=serializer.validated_data['description'],
                    price=serializer.validated_data['price']
                )
                response_serializer = serializers.ListingSerializer(listing)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListingDetailAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        listing = services.get_listing_by_id(pk)
        if not listing:
            return Response({"error": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ListingSerializer(listing)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ListingEditAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        serializer = serializers.ListingSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                listing = services.update_listing(
                    user=request.user,
                    listing_id=pk,
                    **serializer.validated_data
                )
                response_serializer = serializers.ListingSerializer(listing)
                return Response(response_serializer.data, status=status.HTTP_200_OK)
            except PermissionDenied as e:
                return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListingDeleteAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        try:
            services.delete_listing(user=request.user, listing_id=pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
