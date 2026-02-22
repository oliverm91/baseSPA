import 'dart:convert';
import 'package:http/http.dart' as http;
import '../core/constants.dart';
import 'token_storage.dart';

/// Centralized HTTP client that automatically handles token refreshing.
class ApiClient {
  static Future<Map<String, String>> _getHeaders({
    bool requireAuth = true,
  }) async {
    final headers = {'Content-Type': 'application/json'};
    if (requireAuth) {
      final token = await TokenStorage.getAccessToken();
      if (token != null) {
        headers['Authorization'] = 'Bearer $token';
      }
    }
    return headers;
  }

  /// Refreshes the access token using the stored refresh token and save new tokens to safe storage.
  static Future<bool> _refreshToken() async {
    final refreshToken = await TokenStorage.getRefreshToken();
    if (refreshToken == null) return false;

    try {
      final response = await http.post(
        Uri.parse(
          '${AppConstants.apiBaseUrl}/auth/token/refresh/',
        ), // Adjust if dj-rest-auth uses a different refresh URL
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'refresh': refreshToken,
        }), // Adjust if dj-rest-auth uses a different body key
      );
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final newAccessToken = data['access_token'] ?? data['access'];
        // Sometimes refresh also returns a new refresh token
        final newRefreshToken = data['refresh_token'] ?? data['refresh'];

        if (newAccessToken != null) {
          await TokenStorage.saveTokens(
            accessToken: newAccessToken,
            refreshToken: newRefreshToken ?? refreshToken,
          );
          return true;
        }
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  static bool _isTokenExpired(http.Response response) {
    if (response.statusCode != 403 && response.statusCode != 401) return false;

    try {
      final data = jsonDecode(response.body);
      final detail = data['detail']?.toString().toLowerCase() ?? '';
      if (detail.contains('invalid') || detail.contains('expired')) {
        return true;
      }
      final messages = data['messages'];
      if (messages != null && messages is List && messages.isNotEmpty) {
        for (var message in messages) {
          final messageText =
              message['message']?.toString().toLowerCase() ?? '';
          if (messageText.contains('invalid') ||
              messageText.contains('expired')) {
            return true;
          }
        }
      }
      return false;
    } catch (_) {
      return false;
    }
  }

  static Future<http.Response> _sendRequest(
    Uri url, {
    required Future<http.Response> Function(Map<String, String> headers)
    requestFunc,
    bool requireAuth = true,
  }) async {
    final headers = await _getHeaders(requireAuth: requireAuth);
    var response = await requestFunc(headers);
    if (requireAuth && _isTokenExpired(response)) {
      // If token is expired, try to refresh it and retry the request
      final refreshed = await _refreshToken();
      if (refreshed) {
        final newHeaders = await _getHeaders(requireAuth: true);
        response = await requestFunc(newHeaders);
      }
    }
    return response;
  }

  static Future<http.Response> get(Uri url, {bool requireAuth = true}) {
    return _sendRequest(
      url,
      requestFunc: (headers) => http.get(url, headers: headers),
      requireAuth: requireAuth,
    );
  }

  static Future<http.Response> post(
    Uri url, {
    Object? body,
    bool requireAuth = true,
  }) {
    return _sendRequest(
      url,
      requestFunc: (headers) => http.post(url, headers: headers, body: body),
      requireAuth: requireAuth,
    );
  }

  static Future<http.Response> put(
    Uri url, {
    Object? body,
    bool requireAuth = true,
  }) {
    return _sendRequest(
      url,
      requestFunc: (headers) => http.put(url, headers: headers, body: body),
      requireAuth: requireAuth,
    );
  }

  static Future<http.Response> delete(Uri url, {bool requireAuth = true}) {
    return _sendRequest(
      url,
      requestFunc: (headers) => http.delete(url, headers: headers),
      requireAuth: requireAuth,
    );
  }
}
