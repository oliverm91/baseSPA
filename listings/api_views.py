from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from . import services, serializers

class ListingListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """API View to get all active listings."""
        listings = services.get_active_listings()
        serializer = serializers.ListingSerializer(listings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """API View to create a new listing."""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
        serializer = serializers.ListingSerializer(data=request.data)
        if serializer.is_valid():
            try:
                listing = services.create_listing(
                    seller=request.user,
                    title=serializer.validated_data['title'],
                    description=serializer.validated_data['description'],
                    price=serializer.validated_data['price']
                )
                # Return the full listing data using the serializer again
                response_serializer = serializers.ListingSerializer(listing)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            except ValueError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListingDetailView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]

    def get(self, request, pk):
        """API View to get a specific listing."""
        listing = services.get_listing_by_id(pk)
        if not listing:
            return Response({"error": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ListingSerializer(listing)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """API View to update a listing."""
        serializer = serializers.ListingSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            try:
                from django.core.exceptions import PermissionDenied
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

    def delete(self, request, pk):
        """API View to delete a listing."""
        try:
            from django.core.exceptions import PermissionDenied
            services.delete_listing(user=request.user, listing_id=pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
