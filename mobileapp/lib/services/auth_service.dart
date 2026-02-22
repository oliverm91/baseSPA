import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import '../core/constants.dart';

/// Service for handling authentication (Login, Logout, JWT, Registration).
class AuthService {
  final _storage = const FlutterSecureStorage();
  static const _tokenKey = 'jwt_token';

  /// Performs login and stores the JWT.
  Future<bool> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConstants.apiBaseUrl}/auth/login/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'email': email, 'password': password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final token =
            data['access_token'] ??
            data['access']; // dj-rest-auth uses access_token or access
        if (token != null) {
          await _storage.write(key: _tokenKey, value: token);
          return true;
        }
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  /// Performs registration and stores the JWT.
  /// Uses Allauth field names: email, password1, password2.
  Future<bool> register(
    String email,
    String password1,
    String password2,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('${AppConstants.apiBaseUrl}/auth/registration/'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'email': email,
          'password1': password1,
          'password2': password2,
          // Removed 'username' as project uses email as identifier
        }),
      );

      if (response.statusCode == 201 || response.statusCode == 200) {
        final data = jsonDecode(response.body);

        // Safely check for the token keys, as mandatory email verification
        // will not return a token in the 201 response.
        if (data is Map<String, dynamic>) {
          final token = data['access_token'] ?? data['access'];
          if (token != null) {
            await _storage.write(key: _tokenKey, value: token);
          }
        }
        return true; // Registration successful, may require email verification
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  /// Deletes the stored JWT.
  Future<void> logout() async {
    await _storage.delete(key: _tokenKey);
  }

  /// Retrieves the stored JWT.
  Future<String?> getToken() async {
    return await _storage.read(key: _tokenKey);
  }

  /// Checks if the user is currently logged in.
  Future<bool> isLoggedIn() async {
    final token = await getToken();
    return token != null;
  }

  /// Fetches the currently authenticated user's email from the profile endpoint.
  Future<String?> fetchCurrentUserEmail() async {
    try {
      final token = await getToken();
      if (token == null) return null;

      final response = await http.get(
        Uri.parse(
          '${AppConstants.apiBaseUrl}/web/profile/',
        ), // Using the backend endpoint
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'JWT $token',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['email'];
      }
      return null;
    } catch (e) {
      return null;
    }
  }
}
