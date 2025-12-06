import 'package:flutter/material.dart';

class Menu extends StatelessWidget {
  final String? displayName; // Nom d'utilisateur
  final String? email; // E-mail de l'utilisateur

  const Menu({super.key, this.displayName, this.email});

  @override
  Widget build(BuildContext context) {
    // Récupérer la première lettre du prénom de l'utilisateur
    String initial = displayName?.isNotEmpty == true ? displayName![0].toUpperCase() : "U";

    return Drawer(
      child: Column(
        children: [
          // En-tête du Drawer
          DrawerHeader(
            decoration: BoxDecoration(
              gradient: LinearGradient(
                colors: [Colors.red, Colors.grey],
              ),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.start,
              children: [
                CircleAvatar(
                  child: Text(
                    initial, // Afficher la première lettre
                    style: const TextStyle(
                      fontSize: 24.0,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  radius: 40.0,
                  backgroundColor: Colors.grey.shade700,
                ),
                const SizedBox(width: 30.0),
                Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      displayName ?? "Nom d'utilisateur", // Affichage du nom ou d'un nom par défaut
                      style: const TextStyle(
                        fontSize: 18.0,
                        fontWeight: FontWeight.bold,
                        color: Colors.white,
                      ),
                    ),
                    const SizedBox(height: 8.0),
                    Text(
                      email ?? "user@example.com", // Affichage de l'e-mail réel ou d'un e-mail par défaut
                      style: const TextStyle(
                        fontSize: 14.0,
                        color: Colors.white70,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),

          // Contenu du Drawer
          ExpansionTile(
            trailing: const Icon(Icons.arrow_circle_right),
            subtitle: const Text('Fruits/Vegetables'),
            childrenPadding: const EdgeInsets.only(left: 30.0),
            leading: const Icon(Icons.image),
            title: const Text('Image Classification'),
            children: [
              ListTile(
                onTap: () {
                  Navigator.pushNamed(context, '/ann');
                },
                title: const Text('ANN Model'),
              ),
              ListTile(
                onTap: () {
                  Navigator.pushNamed(context, '/cnn');
                },
                title: const Text('CNN Model'),
              ),
            ],
          ),
          const ListTile(
            title: Text('Stock Price Prediction'),
            leading: Icon(Icons.price_change),
          ),
          ListTile(
            title: Text('Vocal Assistance'),
            leading: Icon(Icons.assistant),
            onTap: () {
              Navigator.pushNamed(context, '/audio_recorder');
            },
          ),
        ],
      ),
    );
  }
}