import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'menu.dart'; // Importation du fichier menu.dart

class HomePage extends StatelessWidget {
  final User? user; // Utilisateur connecté

  const HomePage({super.key, required this.user});

  @override
  Widget build(BuildContext context) {
    // Extraction du prénom ou de l'identifiant depuis l'adresse e-mail
    String? displayName = user?.email?.split('@')[0]; // Avant le '@'

    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "Accueil",
          style: TextStyle(color: Colors.white),
        ),
        backgroundColor: Colors.red,
        leading: Builder(
          builder: (context) => IconButton(
            icon: const Icon(Icons.menu),
            onPressed: () => Scaffold.of(context).openDrawer(),
          ),
        ),
      ),
      drawer: Menu(displayName: displayName), // Utilisation du menu importé
      body: Stack(
        children: [
          // Image de fond
          Container(
            decoration: const BoxDecoration(
              image: DecorationImage(
                image: AssetImage('assets/background.jpg'), // Ajoutez votre image ici
                fit: BoxFit.cover,
              ),
            ),
          ),
          // Couche semi-transparente pour le contraste
          Container(
            color: Colors.black.withOpacity(0.5),
          ),
          // Contenu principal
          Center(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                CircleAvatar(
                  radius: 50,
                  backgroundColor: Colors.grey.shade300,
                  child: const Icon(
                    Icons.person,
                    size: 50,
                    color: Colors.red,
                  ),
                ),
                const SizedBox(height: 20),
                Text(
                  "Bienvenue, ${displayName ?? "Invité"}!",
                  style: const TextStyle(
                    fontSize: 24,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 10),
                const Text(
                  "Découvrez vos fonctionnalités ici.",
                  style: TextStyle(
                    fontSize: 16,
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 20),
                ElevatedButton.icon(
                  onPressed: () {
                    // Action à définir
                  },
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.red,
                    padding:
                    const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                  ),
                  icon: const Icon(Icons.arrow_forward, color: Colors.white),
                  label: const Text(
                    "Commencer",
                    style: TextStyle(color: Colors.white, fontSize: 16),
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}