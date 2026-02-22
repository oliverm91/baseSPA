import 'dart:convert';
import 'package:flutter/material.dart';
import '../core/constants.dart';
import '../services/auth_service.dart';
import '../services/api_client.dart';
import '../widgets/app_navbar.dart';
import 'login_screen.dart';

/// Screen for displaying the user's profile.
class ProfileScreen extends StatefulWidget {
  const ProfileScreen({super.key});

  @override
  State<ProfileScreen> createState() => _ProfileScreenState();
}

class _ProfileScreenState extends State<ProfileScreen> {
  final _authService = AuthService();
  Future<Map<String, dynamic>?>? _profileFuture;

  @override
  void initState() {
    super.initState();
    _loadProfile();
  }

  void _loadProfile() {
    setState(() {
      _profileFuture = _fetchProfile();
    });
  }

  Future<Map<String, dynamic>?> _fetchProfile() async {
    try {
      final response = await ApiClient.get(Uri.parse(AppConstants.profileUrl));
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
    } catch (_) {}
    return null;
  }

  void _handleLogout() async {
    await _authService.logout();
    if (mounted) {
      Navigator.of(context).pushAndRemoveUntil(
        MaterialPageRoute(builder: (_) => const LoginScreen()),
        (route) => false,
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: const AppNavbar(),
      body: FutureBuilder<Map<String, dynamic>?>(
        future: _profileFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }

          if (snapshot.hasError || !snapshot.hasData || snapshot.data == null) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Text('Error loading profile.'),
                  const SizedBox(height: 20),
                  ElevatedButton(
                    onPressed: _handleLogout,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red,
                    ),
                    child: const Text(
                      'Logout',
                      style: TextStyle(color: Colors.white),
                    ),
                  ),
                ],
              ),
            );
          }

          final data = snapshot.data!;
          final email = data['email'] ?? 'Unknown Email';
          final listings = data['listings'] as List<dynamic>? ?? [];

          return RefreshIndicator(
            onRefresh: () async {
              _loadProfile();
              await _profileFuture;
            },
            child: ListView(
              padding: const EdgeInsets.all(16),
              children: [
                const SizedBox(height: 20),
                const Icon(
                  Icons.account_circle,
                  size: 80,
                  color: Colors.blueGrey,
                ),
                const SizedBox(height: 16),
                Text(
                  email,
                  style: const TextStyle(
                    fontSize: 20,
                    fontWeight: FontWeight.bold,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 40),
                const Text(
                  'My Active Listings',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const Divider(thickness: 1),
                const SizedBox(height: 8),
                if (listings.isEmpty)
                  const Padding(
                    padding: EdgeInsets.symmetric(vertical: 20),
                    child: Text(
                      'You have no active listings.',
                      style: TextStyle(color: Colors.grey),
                    ),
                  )
                else
                  ...listings.map((item) {
                    final title = item['title'] ?? '';
                    final price = item['price'] ?? '0.00';
                    return Card(
                      margin: const EdgeInsets.only(bottom: 8),
                      child: ListTile(
                        leading: const Icon(Icons.storefront),
                        title: Text(
                          title,
                          style: const TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(
                          '\$$price',
                          style: const TextStyle(color: Colors.green),
                        ),
                      ),
                    );
                  }),
                const SizedBox(height: 40),
                ElevatedButton.icon(
                  onPressed: _handleLogout,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red.shade100,
                    foregroundColor: Colors.red.shade900,
                    padding: const EdgeInsets.symmetric(vertical: 12),
                  ),
                  icon: const Icon(Icons.logout),
                  label: const Text('Logout'),
                ),
                const SizedBox(height: 20),
              ],
            ),
          );
        },
      ),
    );
  }
}
