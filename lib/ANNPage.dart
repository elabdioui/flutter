import 'dart:convert';
import 'dart:html' as html;
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'image_picker_helper.dart';

class ANNPage extends StatefulWidget {
  const ANNPage({super.key});

  @override
  _ANNPageState createState() => _ANNPageState();
}

class _ANNPageState extends State<ANNPage> with SingleTickerProviderStateMixin {
  String? _imageUrl;
  String? _prediction;
  double? _confidence;
  bool _isLoading = false;
  late AnimationController _animationController;
  late Animation<Offset> _slideAnimation;

  final List<Map<String, dynamic>> _examples = [
    {'asset': 'assets/apple.jpg', 'label': 'Apple', 'color': Colors.red},
    {'asset': 'assets/banana.jpg', 'label': 'Banana', 'color': Colors.yellow},
    {'asset': 'assets/tomato.jpg', 'label': 'Tomato', 'color': Colors.redAccent},
    {'asset': 'assets/carrot.jpg', 'label': 'Carrot', 'color': Colors.orange},
    {'asset': 'assets/orange.jpg', 'label': 'Orange', 'color': Colors.deepOrange},
  ];

  @override
  void initState() {
    super.initState();
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 400),
    );
    _slideAnimation = Tween<Offset>(begin: const Offset(0, 1.0), end: Offset.zero).animate(
      CurvedAnimation(parent: _animationController, curve: Curves.easeOut),
    );
    _animationController.forward();
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
    } catch (e) {
      setState(() {
        _prediction = "Erreur";
        _confidence = null;
      });
      _showSnackBar("Erreur: $e", Colors.red);
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
          _showSnackBar("Classification réussie!", Colors.green);
        } else {
          setState(() {
            _prediction = "Erreur serveur";
            _confidence = null;
          });
          _showSnackBar("Erreur serveur: ${response.statusCode}", Colors.red);
        }
      });
    } catch (e) {
      setState(() {
        _prediction = "Erreur";
        _confidence = null;
      });
      _showSnackBar("Erreur: $e", Colors.red);
    }
  }

  void _showSnackBar(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Row(
          children: [
            Icon(
              color == Colors.green ? Icons.check_circle : Icons.error,
              color: Colors.white,
            ),
            const SizedBox(width: 12),
            Expanded(child: Text(message)),
          ],
        ),
        backgroundColor: color,
        behavior: SnackBarBehavior.floating,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10)),
        duration: const Duration(seconds: 2),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          "ANN Model",
          style: TextStyle(fontWeight: FontWeight.w600),
        ),
        backgroundColor: Colors.red.shade700,
        elevation: 0,
        centerTitle: true,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.red.shade700,
              Colors.red.shade400,
            ],
          ),
        ),
        child: SafeArea(
          child: SingleChildScrollView(
            child: Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Titre et description
                  SlideTransition(
                    position: _slideAnimation,
                    child: Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        color: Colors.white,
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.1),
                            blurRadius: 15,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Column(
                        children: [
                          Container(
                            padding: const EdgeInsets.all(16),
                            decoration: BoxDecoration(
                              color: Colors.red.shade50,
                              shape: BoxShape.circle,
                            ),
                            child: Icon(
                              Icons.analytics_outlined,
                              size: 50,
                              color: Colors.red.shade700,
                            ),
                          ),
                          const SizedBox(height: 16),
                          const Text(
                            "Reconnaissez-moi",
                            style: TextStyle(
                              fontSize: 28,
                              fontWeight: FontWeight.bold,
                              color: Colors.black87,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            "Téléchargez une image pour classifier",
                            style: TextStyle(
                              fontSize: 15,
                              color: Colors.grey.shade600,
                            ),
                            textAlign: TextAlign.center,
                          ),
                        ],
                      ),
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Galerie d'exemples
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 15,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Row(
                          children: [
                            Icon(Icons.photo_library,
                                color: Colors.red.shade700, size: 24),
                            const SizedBox(width: 8),
                            const Text(
                              "Classes disponibles",
                              style: TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.black87,
                              ),
                            ),
                          ],
                        ),
                        const SizedBox(height: 16),
                        Wrap(
                          spacing: 12,
                          runSpacing: 12,
                          alignment: WrapAlignment.center,
                          children: _examples
                              .map((example) => _buildExampleChip(
                            example['asset'],
                            example['label'],
                            example['color'],
                          ))
                              .toList(),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 24),

                  // Zone d'upload
                  Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(20),
                      boxShadow: [
                        BoxShadow(
                          color: Colors.black.withOpacity(0.1),
                          blurRadius: 15,
                          offset: const Offset(0, 5),
                        ),
                      ],
                    ),
                    child: Column(
                      children: [
                        // Affichage de l'image
                        Container(
                          height: 200,
                          decoration: BoxDecoration(
                            color: Colors.grey.shade50,
                            borderRadius: BorderRadius.circular(16),
                            border: Border.all(
                              color: _imageUrl != null
                                  ? Colors.red.shade300
                                  : Colors.grey.shade300,
                              width: 2,
                            ),
                          ),
                          child: _imageUrl == null
                              ? Center(
                            child: Column(
                              mainAxisAlignment: MainAxisAlignment.center,
                              children: [
                                Icon(
                                  Icons.cloud_upload_outlined,
                                  size: 60,
                                  color: Colors.grey.shade400,
                                ),
                                const SizedBox(height: 12),
                                Text(
                                  "Choisissez une image",
                                  style: TextStyle(
                                    color: Colors.grey.shade600,
                                    fontSize: 16,
                                  ),
                                ),
                              ],
                            ),
                          )
                              : ClipRRect(
                            borderRadius: BorderRadius.circular(14),
                            child: Image.network(
                              _imageUrl!,
                              fit: BoxFit.cover,
                              width: double.infinity,
                            ),
                          ),
                        ),

                        const SizedBox(height: 20),

                        // Bouton d'upload
                        SizedBox(
                          width: double.infinity,
                          height: 56,
                          child: ElevatedButton.icon(
                            onPressed: _isLoading ? null : pickAndPredictImage,
                            style: ElevatedButton.styleFrom(
                              backgroundColor: Colors.red.shade700,
                              foregroundColor: Colors.white,
                              shape: RoundedRectangleBorder(
                                borderRadius: BorderRadius.circular(16),
                              ),
                              elevation: 4,
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
                                : const Icon(Icons.upload, size: 24),
                            label: Text(
                              _isLoading ? "Analyse..." : "Uploader une image",
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

                  // Résultat
                  if (_prediction != null)
                    Container(
                      padding: const EdgeInsets.all(24),
                      decoration: BoxDecoration(
                        gradient: LinearGradient(
                          colors: [
                            Colors.white,
                            Colors.red.shade50,
                          ],
                        ),
                        borderRadius: BorderRadius.circular(20),
                        boxShadow: [
                          BoxShadow(
                            color: Colors.black.withOpacity(0.1),
                            blurRadius: 15,
                            offset: const Offset(0, 5),
                          ),
                        ],
                      ),
                      child: Column(
                        children: [
                          Icon(
                            Icons.check_circle,
                            size: 60,
                            color: Colors.green.shade400,
                          ),
                          const SizedBox(height: 16),
                          const Text(
                            "Classe prédite",
                            style: TextStyle(
                              fontSize: 16,
                              color: Colors.grey,
                              fontWeight: FontWeight.w500,
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            _prediction!,
                            style: TextStyle(
                              fontSize: 36,
                              fontWeight: FontWeight.bold,
                              color: Colors.red.shade700,
                            ),
                          ),
                          if (_confidence != null) ...[
                            const SizedBox(height: 16),
                            Container(
                              padding: const EdgeInsets.symmetric(
                                horizontal: 16,
                                vertical: 10,
                              ),
                              decoration: BoxDecoration(
                                color: Colors.green.shade50,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(
                                  color: Colors.green.shade200,
                                  width: 1,
                                ),
                              ),
                              child: Text(
                                "Confiance: ${_confidence!.toStringAsFixed(2)}%",
                                style: TextStyle(
                                  fontSize: 18,
                                  fontWeight: FontWeight.w600,
                                  color: Colors.green.shade700,
                                ),
                              ),
                            ),
                          ],
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

  Widget _buildExampleChip(String assetPath, String label, Color color) {
    return Container(
      width: 90,
      child: Column(
        children: [
          Container(
            width: 70,
            height: 70,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: Border.all(color: color, width: 3),
              boxShadow: [
                BoxShadow(
                  color: color.withOpacity(0.3),
                  blurRadius: 8,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: ClipOval(
              child: Image.asset(
                assetPath,
                fit: BoxFit.cover,
              ),
            ),
          ),
          const SizedBox(height: 8),
          Text(
            label,
            style: TextStyle(
              fontSize: 13,
              fontWeight: FontWeight.w600,
              color: Colors.grey.shade700,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}