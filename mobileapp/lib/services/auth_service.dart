import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import 'token_storage.dart';
import 'api_client.dart';

/// Service for handling authentication (Login, Logout, JWT, Registration).
class AuthService {
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
        final accessToken = data['access_token'] ?? data['access'];
        final refreshToken = data['refresh_token'] ?? data['refresh'];
        if (accessToken != null) {
          await TokenStorage.saveTokens(
            accessToken: accessToken,
            refreshToken: refreshToken,
          );
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
          final accessToken = data['access_token'] ?? data['access'];
          final refreshToken = data['refresh_token'] ?? data['refresh'];

          if (accessToken != null) {
            await TokenStorage.saveTokens(
              accessToken: accessToken,
              refreshToken: refreshToken,
            );
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
    await TokenStorage.deleteTokens();
  }

  /// Checks if the user is currently logged in.
  Future<bool> isLoggedIn() async {
    final token = await TokenStorage.getAccessToken();
    return token != null;
  }

  /// Fetches the currently authenticated user's email from the profile endpoint.
  Future<String?> fetchCurrentUserEmail() async {
    try {
      final token = await TokenStorage.getAccessToken();
      if (token == null) return null;

      final response = await ApiClient.get(Uri.parse(AppConstants.profileUrl));

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
