from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from . import services

class ListingListView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        """API View to get all active listings."""
        listings = services.get_active_listings()
        data = [
            {
                "id": lst.id,
                "title": lst.title,
                "description": lst.description,
                "price": str(lst.price),
                "seller_id": lst.seller.id,
                "created_at": lst.created_at.isoformat()
            }
            for lst in listings
        ]
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        """API View to create a new listing."""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
        title = request.data.get("title")
        description = request.data.get("description")
        price = request.data.get("price")

        try:
            listing = services.create_listing(
                seller=request.user,
                title=title,
                description=description,
                price=price
            )
            data = {
                "id": listing.id,
                "title": listing.title,
                "price": str(listing.price)
            }
            return Response(data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ListingDetailView(APIView):
    def put(self, request, pk):
        """API View to update a listing."""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            from django.core.exceptions import PermissionDenied
            listing = services.update_listing(
                user=request.user,
                listing_id=pk,
                title=request.data.get("title"),
                description=request.data.get("description"),
                price=request.data.get("price")
            )
            data = {
                "id": listing.id,
                "title": listing.title,
                "description": listing.description,
                "price": str(listing.price)
            }
            return Response(data, status=status.HTTP_200_OK)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """API View to delete a listing."""
        if not request.user.is_authenticated:
            return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
            
        try:
            from django.core.exceptions import PermissionDenied
            services.delete_listing(user=request.user, listing_id=pk)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except PermissionDenied as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
