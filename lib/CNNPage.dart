import 'dart:convert';
import 'package:flutter/material.dart';
import 'dart:html' as html;
import 'package:http/http.dart' as http;
import 'image_picker_helper.dart'; // Import de la classe partagée

class CNNPage extends StatefulWidget {
  const CNNPage({super.key});

  @override
  _CNNPageState createState() => _CNNPageState();
}

class _CNNPageState extends State<CNNPage> {
  String? _imageUrl; // URL de l'image sélectionnée
  String? _prediction; // Résultat de la prédiction
  double? _confidence; // Niveau de confiance
  bool _isLoading = false; // Indicateur de chargement

  // Méthode pour sélectionner une image et prédire
  Future<void> pickAndPredictImage() async {
    try {
      setState(() {
        _isLoading = true;
      });

      // Utilisation de la classe partagée pour sélectionner l'image
      final result = await ImagePickerHelper.pickImage();
      final html.File file = result['file'];
      final String imageUrl = result['imageUrl'];

      setState(() {
        _imageUrl = imageUrl;
      });

      // Prédire l'image
      await predictImage(file);
    } catch (e) {
      setState(() {
        _prediction = "Erreur : $e";
        _confidence = null;
      });
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

  // Méthode pour prédire l'image
  Future<void> predictImage(html.File file) async {
    try {
      final reader = html.FileReader();
      reader.readAsArrayBuffer(file);

      reader.onLoadEnd.listen((event) async {
        final request = http.MultipartRequest(
          'POST',
          Uri.parse('http://127.0.0.1:8000/predict'),
        );

        request.files.add(
          http.MultipartFile.fromBytes(
            'file',
            reader.result as List<int>,
            filename: file.name,
          ),
        );

        final response = await request.send();

        if (response.statusCode == 200) {
          final responseData = await http.Response.fromStream(response);
          final data = jsonDecode(responseData.body);
          setState(() {
            _prediction = data['prediction']['label'];
            _confidence = double.tryParse(data['prediction']['confidence'].replaceAll('%', ''));
          });
        } else {
          setState(() {
            _prediction = "Erreur serveur : ${response.statusCode}";
            _confidence = null;
          });
        }
      });
    } catch (e) {
      setState(() {
        _prediction = "Erreur : $e";
        _confidence = null;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text("CNN Model"),
        backgroundColor: Colors.deepOrange,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Cercle contenant l'image sélectionnée ou message par défaut
            _imageUrl == null
                ? const Text("Aucune image sélectionnée")
                : CircleAvatar(
              backgroundImage: NetworkImage(_imageUrl!),
              radius: 80,
            ),
            const SizedBox(height: 20),

            // Bouton pour uploader une image
            ElevatedButton(
              onPressed: _isLoading ? null : pickAndPredictImage,
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.deepOrange,
                padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
              ),
              child: _isLoading
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Text("Uploader une image"),
            ),

            const SizedBox(height: 20),

            // Résultat de la prédiction
            Text(
              _prediction == null
                  ? "La prédiction apparaîtra ici"
                  : "Classe prédite : $_prediction\nConfiance : ${_confidence?.toStringAsFixed(2)}%",
              style: const TextStyle(fontSize: 18),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }
}