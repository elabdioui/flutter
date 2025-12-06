import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:project_flutter_model/ANNPage.dart';
import 'package:project_flutter_model/AudioRecorderPage.dart';
import 'package:project_flutter_model/CNNPage.dart';
import 'HomePage.dart';
import 'firebase_options.dart';
import 'login_screen.dart';


void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp(
    options: DefaultFirebaseOptions.currentPlatform, // Utilisation des options générées
  );
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Firebase Auth App',
      theme: ThemeData(
        primarySwatch: Colors.deepPurple,
      ),
      initialRoute: FirebaseAuth.instance.currentUser == null ? '/login' : '/home',
      routes: {
        // Routes pour l'authentification
        '/login': (context) => LoginScreen(),
        '/home': (context) => HomePage(user: FirebaseAuth.instance.currentUser),

        // Routes supplémentaires pour la navigation
        '/ann': (context) => const ANNPage(),
        '/cnn': (context) => const CNNPage(),
        '/audio_recorder': (context) => AudioRecorderPage(), // Route pour AudioRecorderPage

      },
    );
  }
}
