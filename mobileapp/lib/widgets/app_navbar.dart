import 'package:flutter/material.dart';
import '../services/auth_service.dart';
import '../screens/profile_screen.dart';
import '../screens/login_screen.dart';
import '../screens/marketplace_screen.dart';

/// Reusable Navbar for the application.
class AppNavbar extends StatelessWidget implements PreferredSizeWidget {
  const AppNavbar({super.key});

  @override
  Size get preferredSize => const Size.fromHeight(kToolbarHeight);

  @override
  Widget build(BuildContext context) {
    final authService = AuthService();
    final isAtProfile =
        context.findAncestorWidgetOfExactType<ProfileScreen>() != null;
    final isAtLogin =
        context.findAncestorWidgetOfExactType<LoginScreen>() != null;
    final isAtMarketplace =
        context.findAncestorWidgetOfExactType<MarketplaceScreen>() != null;

    return AppBar(
      // Only show back button on Profile Screen
      automaticallyImplyLeading: isAtProfile,
      title: GestureDetector(
        onTap: () {
          if (!isAtMarketplace) {
            Navigator.of(context).pushAndRemoveUntil(
              MaterialPageRoute(builder: (_) => const MarketplaceScreen()),
              (route) => false,
            );
          }
        },
        child: const Text(
          'BaseSPA',
          style: TextStyle(fontWeight: FontWeight.bold, letterSpacing: 1.2),
        ),
      ),
      actions: [
        // Hide account icon on Login Screen
        if (!isAtLogin)
          IconButton(
            icon: const Icon(Icons.account_circle, size: 30),
            onPressed: () async {
              final loggedIn = await authService.isLoggedIn();
              if (context.mounted) {
                if (loggedIn) {
                  if (!isAtProfile) {
                    Navigator.of(context).push(
                      MaterialPageRoute(builder: (_) => const ProfileScreen()),
                    );
                  }
                } else {
                  Navigator.of(context).push(
                    MaterialPageRoute(builder: (_) => const LoginScreen()),
                  );
                }
              }
            },
          ),
        const SizedBox(width: 8),
      ],
    );
  }
}
