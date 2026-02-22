/// Base data model for Listings.
class Listing {
  final int id;
  final String title;
  final String description;
  final double price;
  final String sellerEmail;
  final DateTime createdAt;
  final bool isActive;

  Listing({
    required this.id,
    required this.title,
    required this.description,
    required this.price,
    required this.sellerEmail,
    required this.createdAt,
    required this.isActive,
  });

  factory Listing.fromJson(Map<String, dynamic> json) {
    return Listing(
      id: json['id'],
      title: json['title'],
      description: json['description'] ?? '',
      price: double.parse(json['price'].toString()),
      sellerEmail: json['seller_email'] ?? '',
      createdAt: DateTime.parse(json['created_at']),
      isActive: json['is_active'] ?? true,
    );
  }
}
