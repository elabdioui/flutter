import 'package:google_generative_ai/google_generative_ai.dart';

class GeminiService {
  final GenerativeModel _model;

  // Initialisation du modèle avec une clé API
  GeminiService(String apiKey)
      : _model = GenerativeModel(
    model: 'gemini-1.5-flash', // Modèle valide
    apiKey: apiKey,
  );

  // Méthode pour générer du contenu basé sur un prompt
  Future<String> generateResponse(String prompt) async {
    try {
      // Utilisez la méthode generateContent avec le modèle
      final response = await _model.generateContent([
        Content.text(prompt),
      ]);

      // Retournez le texte généré
      return response.text ?? 'Aucune réponse générée.';
    } catch (e) {
      print('Erreur lors de la génération du contenu : $e');
      return 'Erreur : Impossible de générer du contenu.';
    }
  }
}