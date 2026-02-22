from rest_framework import serializers
from .models import Listing

class ListingSerializer(serializers.ModelSerializer):
    seller_email = serializers.EmailField(source='seller.email', read_only=True)

    class Meta:
        model = Listing
        fields = ['id', 'title', 'description', 'price', 'seller', 'seller_email', 'created_at']
        read_only_fields = ['seller', 'created_at']
