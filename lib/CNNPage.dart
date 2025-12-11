import 'dart:convert';
import 'package:flutter/material.dart';
import 'dart:html' as html;
import 'package:http/http.dart' as http;
import 'image_picker_helper.dart';

class CNNPage extends StatefulWidget {
  const CNNPage({super.key});

  @override
  _CNNPageState createState() => _CNNPageState();
}

class _CNNPageState extends State<CNNPage> with SingleTickerProviderStateMixin {
  String? _imageUrl;
  String? _prediction;
  double? _confidence;
  bool _isLoading = false;
  late AnimationController _animationController;
  late Animation<double> _scaleAnimation;

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 300),
    );
    _scaleAnimation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOutBack),
    );
  }

  @override
  void dispose() {
    _animationController.dispose();
    super.dispose();
  }

  Future<void> pickAndPredictImage() async {
    try {
      setState(() {
        _isLoading = true;
        _prediction = null;
        _confidence = null;
      });

      final result = await ImagePickerHelper.pickImage();
      final html.File file = result['file'];
      final String imageUrl = result['imageUrl'];

      setState(() {
        _imageUrl = imageUrl;
      });

      await predictImage(file);
      _animationController.forward(from: 0.0);
    } catch (e) {
      setState(() {
        _prediction = "Erreur";
        _confidence = null;
      });
      _showErrorSnackBar("Erreur lors de la sélection: $e");
    } finally {
      setState(() {
        _isLoading = false;
      });
    }
  }

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
            _confidence = double.tryParse(
                data['prediction']['confidence'].replaceAll('%', ''));
          });
        } else {
          setState(() {
            _prediction = "Erreur serveur";
            _confidence = null;
          });
          _showErrorSnackBar("Erreur serveur: ${response.statusCode}");
        }
      });
    } catch (e) {
      setState(() {
        _prediction = "Erreur";
        _confidence = null;
      });
      _showErrorSnackBar("Erreur de prédiction: $e");
    }
  }

  void _showErrorSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.red.shade400,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
      ),
    );
  }

  Color _getConfidenceColor() {
    if (_confidence == null) return Colors.grey;
    if (_confidence! >= 80) return Colors.green;
    if (_confidence! >= 60) return Colors.orange;
    return Colors.red;
  }

  IconData _getPredictionIcon() {
    if (_prediction == null) return Icons.help_outline;
    switch (_prediction!.toLowerCase()) {
      case 'apple':
        return Icons.apple;
      case 'banana':
        return Icons.bakery_dining;
      case 'orange':
        return Icons.circle;
      case 'carrot':
        return Icons.eco;
      case 'tomato':
        return Icons.circle;
      default:
        return Icons.category;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "CNN Model",
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        backgroundColor: Colors.deepOrange,
        elevation: 0,
        centerTitle: true,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.deepOrange,
              Colors.orange.shade300,
            ],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                children: [
                  // Carte d'image
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(24),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 20,
                          offset: const Offset(0, 10),
                        ),
                      ],
                    ),
                    child: Column(
                      children: [
                        // Zone d'affichage de l'image
                        Container(
                          height: 250,
                          width: double.infinity,
                          decoration: BoxDecoration(
                            color: Colors.grey.shade100,
                            borderRadius: BorderRadius.circular(20),
                            border: Border.all(
                              color: Colors.grey.shade300,
                              width: 2,
                              style: BorderStyle.solid,
                            ),
                          ),
                          child: _imageUrl == null
                              ? Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.add_photo_alternate_outlined,
                                size: 80,
                                color: Colors.grey.shade400,
                              ),
                              const SizedBox(height: 16),
                              Text(
                                "Aucune image sélectionnée",
                                style: TextStyle(
                                  fontSize: 16,
                                  color: Colors.grey.shade600,
                                  fontWeight: FontWeight.w500,
                                ),
                              ),
                            ],
                          )
                              : ClipRRect(
                            borderRadius: BorderRadius.circular(18),
                            child: Image.network(
                              _imageUrl!,
                              fit: BoxFit.cover,
                              loadingBuilder: (context, child, progress) {
                                if (progress == null) return child;
                                return Center(
                                  child: CircularProgressIndicator(
                                    color: Colors.deepOrange,
                                  ),
                                );
                              },
                            ),
                          ),
                        ),

                        const SizedBox(height: 24),

                        // Bouton d'upload
                        SizedBox(
                          width: double.infinity,
                          height: 56,
                          child: ElevatedButton.icon(
                            onPressed: _isLoading ? null : pickAndPredictImage,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.deepOrange,
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16),
                              ),
                              elevation: 4,
                              disabledBackgroundColor: Colors.grey.shade300,
                            ),
                            icon: _isLoading
                                ? const SizedBox(
                              width: 24,
                              height: 24,
                              child: CircularProgressIndicator(
                                color: Colors.white,
                                strokeWidth: 3,
                              ),
                            )
                                : const Icon(Icons.upload_file, size: 24),
                            label: Text(
                              _isLoading
                                  ? "Analyse en cours..."
                                  : "Uploader une image",
                              style: const TextStyle(
                                fontSize: 16,
                                fontWeight: FontWeight.w600,
                              ),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Carte de résultat
                  if (_prediction != null || _isLoading)
                    ScaleTransition(
                      scale: _scaleAnimation,
                      child: Container(
                        padding: const EdgeInsets.all(24),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          borderRadius: BorderRadius.circular(24),
                          boxShadow: [
                            BoxShadow(
                              color: Colors.black.withOpacity(0.1),
                              blurRadius: 20,
                              offset: const Offset(0, 10),
                            ),
                          ],
                        ),
                        child: Column(
                          children: [
                            Container(
                              padding: const EdgeInsets.all(16),
                              decoration: BoxDecoration(
                                color: _getConfidenceColor().withOpacity(0.1),
                                shape: BoxShape.circle,
                              ),
                              child: Icon(
                                _getPredictionIcon(),
                                size: 60,
                                color: _getConfidenceColor(),
                              ),
                            ),
                            const SizedBox(height: 20),
                            const Text(
                              "Résultat de la prédiction",
                              style: TextStyle(
                                fontSize: 16,
                                color: Colors.grey,
                                fontWeight: FontWeight.w500,
                              ),
                            ),
                            const SizedBox(height: 12),
                            Text(
                              _prediction ?? "En attente...",
                              style: TextStyle(
                                fontSize: 32,
                                fontWeight: FontWeight.bold,
                                color: _getConfidenceColor(),
                              ),
                              textAlign: TextAlign.center,
                            ),
                            if (_confidence != null) ...[
                              const SizedBox(height: 20),
                              Container(
                                padding: const EdgeInsets.symmetric(
                                  horizontal: 20,
                                  vertical: 12,
                                ),
                                decoration: BoxDecoration(
                                  color: _getConfidenceColor().withOpacity(0.1),
                                  borderRadius: BorderRadius.circular(12),
                                ),
                                child: Row(
                                  mainAxisSize: MainAxisSize.min,
                                  children: [
                                    Icon(
                                      Icons.verified,
                                      color: _getConfidenceColor(),
                                      size: 20,
                                    ),
                                    const SizedBox(width: 8),
                                    Text(
                                      "Confiance: ${_confidence!.toStringAsFixed(2)}%",
                                      style: TextStyle(
                                        fontSize: 18,
                                        fontWeight: FontWeight.w600,
                                        color: _getConfidenceColor(),
                                      ),
                                    ),
                                  ],
                                ),
                              ),
                              const SizedBox(height: 16),
                              // Barre de progression
                              ClipRRect(
                                borderRadius: BorderRadius.circular(10),
                                child: LinearProgressIndicator(
                                  value: _confidence! / 100,
                                  backgroundColor: Colors.grey.shade200,
                                  valueColor: AlwaysStoppedAnimation<Color>(
                                    _getConfidenceColor(),
                                  ),
                                  minHeight: 8,
                                ),
                              ),
                            ],
                          ],
                        ),
                      ),
                    ),

                  const SizedBox(height: 24),

                  // Info card
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white.withOpacity(0.9),
                      borderRadius: BorderRadius.circular(16),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          Icons.info_outline,
                          color: Colors.deepOrange,
                          size: 24,
                        ),
                        const SizedBox(width: 12),
                        Expanded(
                          child: Text(
                            "Utilisez le modèle CNN pour classifier des fruits et légumes",
                            style: TextStyle(
                              fontSize: 14,
                              color: Colors.grey.shade700,
                              height: 1.4,
                            ),
                          ),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}