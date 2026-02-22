import 'dart:convert';
import '../core/constants.dart';
import '../models/listing.dart';
import 'api_client.dart';

/// Service for handling Marketplace Listings.
class ListingService {
  /// Fetches all active listings from the marketplace.
  Future<List<Listing>> fetchListings() async {
    try {
      final response = await ApiClient.get(
        Uri.parse(AppConstants.listingsUrl),
        requireAuth: false,
      );
      if (response.statusCode == 200) {
        final List<dynamic> data = jsonDecode(response.body);
        return data.map((item) => Listing.fromJson(item)).toList();
      }
      return [];
    } catch (e) {
      return [];
    }
  }

  /// Creates a new listing.
  Future<bool> createListing(
    String title,
    String description,
    double price,
  ) async {
    try {
      final response = await ApiClient.post(
        Uri.parse('${AppConstants.listingsUrl}create/'),
        body: jsonEncode({
          'title': title,
          'description': description,
          'price': price,
        }),
      );

      return response.statusCode == 201;
    } catch (e) {
      return false;
    }
  }

  /// Updates an existing listing.
  Future<bool> updateListing(
    int id,
    String title,
    String description,
    double price,
  ) async {
    try {
      final response = await ApiClient.put(
        Uri.parse('${AppConstants.listingsUrl}$id/edit/'),
        body: jsonEncode({
          'title': title,
          'description': description,
          'price': price,
        }),
      );

      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }

  /// Deletes a listing.
  Future<bool> deleteListing(int id) async {
    try {
      final response = await ApiClient.delete(
        Uri.parse('${AppConstants.listingsUrl}$id/delete/'),
      );

      return response.statusCode == 204;
    } catch (e) {
      return false;
    }
  }
}
