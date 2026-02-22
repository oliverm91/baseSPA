import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../main.dart';
import '../core/constants.dart';
import '../screens/login_screen.dart';
import 'token_storage.dart';
import 'api_client.dart';

/// Result of an authentication operation.
class AuthResult {
  final bool success;
  final String? errorMessage;

  AuthResult({required this.success, this.errorMessage});
}

/// Service for handling authentication (Login, Logout, JWT, Registration).
class AuthService {
  // ... (keep the rest of the file unmodified, we're just updating the top imports)
  /// Performs login and stores the JWT.
  Future<AuthResult> login(String email, String password) async {
    try {
      final response = await http
          .post(
            Uri.parse('${AppConstants.apiBaseUrl}/auth/login/'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({'email': email, 'password': password}),
          )
          .timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final accessToken = data['access_token'] ?? data['access'];
        final refreshToken = data['refresh_token'] ?? data['refresh'];
        if (accessToken != null) {
          await TokenStorage.saveTokens(
            accessToken: accessToken,
            refreshToken: refreshToken,
          );
          return AuthResult(success: true);
        }
      } else if (response.statusCode == 400 || response.statusCode == 401) {
        return AuthResult(
          success: false,
          errorMessage: 'Invalid credentials. Please check and try again.',
        );
      }
      return AuthResult(
        success: false,
        errorMessage: 'Server returned error: ${response.statusCode}',
      );
    } catch (e) {
      final errorStr = e.toString().toLowerCase();
      if (errorStr.contains('socket') ||
          errorStr.contains('connection') ||
          errorStr.contains('failed to connect')) {
        return AuthResult(
          success: false,
          errorMessage: 'Connection error. Is the server running?',
        );
      }
      return AuthResult(success: false, errorMessage: 'An error occurred: $e');
    }
  }

  /// Performs registration and stores the JWT.
  /// Uses Allauth field names: email, password1, password2.
  Future<AuthResult> register(
    String email,
    String password1,
    String password2,
  ) async {
    try {
      final response = await http
          .post(
            Uri.parse('${AppConstants.apiBaseUrl}/auth/registration/'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'email': email,
              'password1': password1,
              'password2': password2,
              // Removed 'username' as project uses email as identifier
            }),
          )
          .timeout(const Duration(seconds: 10));

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
        return AuthResult(success: true);
      } else if (response.statusCode == 400) {
        return AuthResult(
          success: false,
          errorMessage: 'Registration failed. Please check your data.',
        );
      }
      return AuthResult(
        success: false,
        errorMessage: 'Server returned error: ${response.statusCode}',
      );
    } catch (e) {
      final errorStr = e.toString().toLowerCase();
      if (errorStr.contains('socket') ||
          errorStr.contains('connection') ||
          errorStr.contains('failed to connect')) {
        return AuthResult(
          success: false,
          errorMessage: 'Connection error. Is the server running?',
        );
      }
      return AuthResult(success: false, errorMessage: 'An error occurred: $e');
    }
  }

  /// Deletes the stored JWT.
  Future<void> logout() async {
    await TokenStorage.deleteTokens();
  }

  /// Force log out the user when authentication fails and alert them.
  static Future<void> forceLogout(String title, String message) async {
    // 1. Clear tokens
    await TokenStorage.deleteTokens();

    // 2. Access the global navigator context
    final context = navigatorKey.currentContext;
    if (context == null) return;

    // 3. Show dialog
    if (context.mounted) {
      showDialog(
        context: context,
        barrierDismissible: false,
        builder: (dialogContext) => AlertDialog(
          title: Text(title),
          content: Text(message),
          actions: [
            TextButton(
              onPressed: () {
                Navigator.of(dialogContext).pop();
                // 4. Navigate directly to LoginScreen
                Navigator.of(context).pushAndRemoveUntil(
                  MaterialPageRoute(builder: (_) => const LoginScreen()),
                  (route) => false,
                );
              },
              child: const Text('OK'),
            ),
          ],
        ),
      );
    }
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
