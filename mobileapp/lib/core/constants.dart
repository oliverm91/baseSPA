import 'dart:io';

/// App-wide constants and configuration.
class AppConstants {
  static const String appName = 'BaseSPA Mobile';

  static String get apiBaseUrl {
    if (Platform.isAndroid) {
      return 'http://10.0.2.2:8000';
    } else {
      return 'http://localhost:8000';
    }
  }

  // Auth: Has its own prefix per request
  static String get authUrl => '$apiBaseUrl/auth/';

  // Global API Consolidation (/api/)
  static String get listingsUrl => '$apiBaseUrl/api/marketplace/';
  static String get profileUrl => '$apiBaseUrl/api/profile/';
}
