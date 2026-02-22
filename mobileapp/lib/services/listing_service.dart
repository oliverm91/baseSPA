import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../core/constants.dart';
import '../models/listing.dart';

/// Service for handling Marketplace Listings.
class ListingService {
  final _storage = const FlutterSecureStorage();
  static const _tokenKey = 'jwt_token';

  Future<Map<String, String>> _getAuthHeaders() async {
    final token = await _storage.read(key: _tokenKey);
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'JWT $token',
    };
  }

  /// Fetches all active listings from the marketplace.
  Future<List<Listing>> fetchListings() async {
    try {
      final response = await http.get(Uri.parse(AppConstants.listingsUrl));
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
      final headers = await _getAuthHeaders();
      final response = await http.post(
        Uri.parse('${AppConstants.listingsUrl}create/'),
        headers: headers,
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
      final headers = await _getAuthHeaders();
      final response = await http.put(
        Uri.parse('${AppConstants.listingsUrl}$id/edit/'),
        headers: headers,
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
      final headers = await _getAuthHeaders();
      final response = await http.delete(
        Uri.parse('${AppConstants.listingsUrl}$id/delete/'),
        headers: headers,
      );

      return response.statusCode == 204;
    } catch (e) {
      return false;
    }
  }
}
