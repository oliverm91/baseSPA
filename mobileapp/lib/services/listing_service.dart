import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import '../models/listing.dart';

/// Service for handling Marketplace Listings.
class ListingService {
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
}
