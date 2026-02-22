import 'package:flutter/material.dart';
import '../services/listing_service.dart';
import '../models/listing.dart';
import '../widgets/app_navbar.dart';
import '../services/auth_service.dart';
import 'login_screen.dart';
import 'signup_screen.dart';
import 'listing_form_screen.dart';

/// Screen for displaying the Marketplace items.
class MarketplaceScreen extends StatefulWidget {
  const MarketplaceScreen({super.key});

  @override
  State<MarketplaceScreen> createState() => _MarketplaceScreenState();
}

class _MarketplaceScreenState extends State<MarketplaceScreen> {
  final _listingService = ListingService();
  final _authService = AuthService();

  late Future<List<Listing>> _listingsFuture;
  String? _currentUserEmail;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _loadData() {
    setState(() {
      _listingsFuture = _listingService.fetchListings();
    });
    _authService.fetchCurrentUserEmail().then((email) {
      if (mounted) {
        setState(() => _currentUserEmail = email);
      }
    });
  }

  Future<void> _handleDelete(int id) async {
    final confirm = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Delete Listing'),
        content: const Text('Are you sure you want to delete this listing?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            style: TextButton.styleFrom(foregroundColor: Colors.red),
            child: const Text('Delete'),
          ),
        ],
      ),
    );

    if (confirm == true) {
      final success = await _listingService.deleteListing(id);
      if (mounted) {
        if (success) {
          _loadData(); // Reload the list
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('Listing deleted successfully')),
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Failed to delete listing'),
              backgroundColor: Colors.red,
            ),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppNavbar(onRefresh: _loadData),
      body: FutureBuilder<List<Listing>>(
        future: _listingsFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return const Center(child: Text('Error loading listings'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('No active listings found'));
          }

          final listings = snapshot.data!;
          return RefreshIndicator(
            onRefresh: () async {
              _loadData();
              // Wait for the future to finish
              await _listingsFuture;
            },
            child: ListView.builder(
              itemCount: listings.length,
              padding: const EdgeInsets.all(8),
              itemBuilder: (context, index) {
                final listing = listings[index];
                return Card(
                  elevation: 4,
                  margin: const EdgeInsets.symmetric(vertical: 8),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Padding(
                    padding: const EdgeInsets.all(16.0),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          listing.title,
                          style: const TextStyle(
                            fontSize: 18,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          listing.description,
                          maxLines: 2,
                          overflow: TextOverflow.ellipsis,
                          style: TextStyle(color: Colors.grey[600]),
                        ),
                        const SizedBox(height: 12),
                        Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            Text(
                              '\$${listing.price.toStringAsFixed(2)}',
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.bold,
                                color: Colors.green,
                              ),
                            ),
                            Text(
                              listing.sellerEmail,
                              style: const TextStyle(
                                fontSize: 12,
                                fontStyle: FontStyle.italic,
                              ),
                            ),
                          ],
                        ),
                        if (_currentUserEmail != null &&
                            _currentUserEmail == listing.sellerEmail) ...[
                          const Divider(height: 24),
                          Row(
                            mainAxisAlignment: MainAxisAlignment.end,
                            children: [
                              TextButton.icon(
                                onPressed: () {
                                  Navigator.of(context).push(
                                    MaterialPageRoute(
                                      builder: (_) => ListingFormScreen(
                                        existingListing: listing,
                                      ),
                                    ),
                                  );
                                },
                                icon: const Icon(Icons.edit, size: 18),
                                label: const Text('Edit'),
                              ),
                              TextButton.icon(
                                onPressed: () => _handleDelete(listing.id),
                                icon: const Icon(Icons.delete, size: 18),
                                label: const Text('Delete'),
                                style: TextButton.styleFrom(
                                  foregroundColor: Colors.red,
                                ),
                              ),
                            ],
                          ),
                        ],
                      ],
                    ),
                  ),
                );
              },
            ),
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () async {
          final authService = AuthService();
          final loggedIn = await authService.isLoggedIn();

          if (mounted) {
            if (loggedIn) {
              Navigator.of(context).push(
                MaterialPageRoute(builder: (_) => const ListingFormScreen()),
              );
            } else {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: const Text('Authentication Required'),
                  content: const Text(
                    'Please login or sign up to create a listing.',
                  ),
                  actions: [
                    TextButton(
                      onPressed: () {
                        Navigator.pop(context);
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => const LoginScreen(),
                          ),
                        );
                      },
                      child: const Text('Login'),
                    ),
                    TextButton(
                      onPressed: () {
                        Navigator.pop(context);
                        Navigator.of(context).push(
                          MaterialPageRoute(
                            builder: (_) => const SignUpScreen(),
                          ),
                        );
                      },
                      child: const Text('Sign Up'),
                    ),
                  ],
                ),
              );
            }
          }
        },
        child: const Icon(Icons.add),
      ),
    );
  }
}
