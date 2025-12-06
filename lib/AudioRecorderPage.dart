import 'package:flutter/material.dart';
import 'package:speech_to_text/speech_recognition_result.dart';
import 'package:speech_to_text/speech_to_text.dart';
import 'gemini_service.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Reconnaissance Vocale avec Gemini',
      theme: ThemeData(
        primarySwatch: Colors.deepPurple,
      ),
      home: AudioRecorderPage(),
    );
  }
}

class AudioRecorderPage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<AudioRecorderPage> {
  final SpeechToText _speechToText = SpeechToText();//Instance de la classe SpeechToText pour gérer la reconnaissance vocale.
  final GeminiService _geminiService = GeminiService('AIzaSyC9jvdG_YVK3Q5Rs2UoyDQG9hpb3TKuhfM'); // Remplacez par votre clé API
  bool _speechEnabled = false;//Booléen indiquant si la reconnaissance vocale est disponible.
  String _lastWords = '';//Contient le texte reconnu par la reconnaissance vocale.
  String _geminiResponse = ''; //Contient la réponse générée par le service Gemini.

  @override
  void initState() {
    super.initState();
    _initSpeech();//Méthode appelée pour initialiser la reconnaissance vocale.

  }

  /// Initialiser la reconnaissance vocale
  void _initSpeech() async {
    bool hasPermission = await _speechToText.initialize();//Initialise la reconnaissance vocale et demande les permissions nécessaires.
    setState(() {
      _speechEnabled = hasPermission;//Met à jour _speechEnabled avec le résultat de la vérification.
    });

    if (!hasPermission) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Permission du microphone refusée.')),
      );
    }
  }

  /// Commencer l'écoute avec vérification des permissions
  void _startListening() async {
    if (_speechEnabled && !_speechToText.isListening) {//Vérifie si la reconnaissance vocale est disponible et si elle n'est pas déjà en cours.
      await _speechToText.listen(onResult: _onSpeechResult);//Démarre l'écoute et associe la méthode _onSpeechResult pour traiter les résultats.
      setState(() {});
    } else if (!_speechEnabled) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('La reconnaissance vocale n\'est pas disponible.')),
      );
    }
  }

  /// Arrêter l'écoute et envoyer le texte à Gemini
  void _stopListening() async {
    await _speechToText.stop();
    _sendToGemini(_lastWords); // Envoyer le texte reconnu à Gemini
    setState(() {});
  }

  /// Gestion des résultats de la reconnaissance vocale
  void _onSpeechResult(SpeechRecognitionResult result) {//SpeechRecognitionResult Résultat renvoyé par la reconnaissance vocale.

    setState(() {
      _lastWords = result.recognizedWords;//Stocke les mots reconnus.
    });
  }

  /// Envoyer le texte reconnu à Gemini pour générer une réponse
  List<String> _geminiResponses = []; // Liste pour stocker les réponses

  void _sendToGemini(String prompt) async {
    if (prompt.isEmpty) {
      setState(() {
        _geminiResponse = 'Aucun texte à envoyer.';
      });
      return;
    }

    setState(() {
      _geminiResponse = 'Génération de la réponse...';
    });

    final response = await _geminiService.generateResponse(prompt);
    setState(() {
      _geminiResponse = response;
      _geminiResponses.add(response); // Ajouter la réponse à l'historique
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Assistant Vocal avec Gemini'),
        backgroundColor: Colors.deepPurple,
        elevation: 5,
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            colors: [Colors.deepPurple, Colors.deepPurpleAccent],
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
          ),
        ),
        child: SingleChildScrollView(
          child: Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                // Section pour le texte reconnu
                Container(
                  padding: EdgeInsets.symmetric(vertical: 16),
                  child: Text(
                    'Texte Reconnu',
                    style: TextStyle(
                      fontSize: 24.0,
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ),
                Card(
                  elevation: 8,
                  margin: EdgeInsets.symmetric(vertical: 8),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Container(
                    padding: EdgeInsets.all(16),
                    decoration: BoxDecoration(
                      borderRadius: BorderRadius.circular(12),
                      gradient: LinearGradient(
                        colors: [
                          Colors.white,
                          Colors.purple[50]!,
                        ],
                        begin: Alignment.topLeft,
                        end: Alignment.bottomRight,
                      ),
                    ),
                    child: Center(
                      child: Text(
                        _speechToText.isListening
                            ? _lastWords
                            : _speechEnabled
                            ? 'Appuyez sur "Start" pour commencer à écouter...'
                            : 'La reconnaissance vocale n\'est pas disponible.',
                        style: TextStyle(
                          fontSize: 16,
                          color: Colors.black87,
                          fontStyle: FontStyle.italic,
                        ),
                        textAlign: TextAlign.center,
                      ),
                    ),
                  ),
                ),
                if (_geminiResponse.isNotEmpty)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      SizedBox(height: 16),
                      Text(
                        'Réponse Actuelle',
                        style: TextStyle(
                          fontSize: 20,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      Card(
                        elevation: 10,
                        shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12),
                        ),
                        child: Container(
                          margin: EdgeInsets.symmetric(vertical: 8),
                          padding: EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            color: Colors.grey[200],
                            borderRadius: BorderRadius.circular(12),
                          ),
                          child: Text(
                            _geminiResponse,
                            style: TextStyle(fontSize: 16, color: Colors.black87),
                          ),
                        ),
                      ),
                    ],
                  ),

                // Historique des Réponses
                if (_geminiResponses.isNotEmpty)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.stretch,
                    children: [
                      SizedBox(height: 16),
                      Text(
                        'Historique des Réponses',
                        style: TextStyle(
                          fontSize: 20,
                          color: Colors.white,
                          fontWeight: FontWeight.bold,
                        ),
                        textAlign: TextAlign.center,
                      ),
                      ListView.builder(
                        shrinkWrap: true,
                        physics: NeverScrollableScrollPhysics(),
                        itemCount: _geminiResponses.length,
                        itemBuilder: (context, index) {
                          return Card(
                            elevation: 5,
                            margin:
                            EdgeInsets.symmetric(vertical: 8, horizontal: 16),
                            child: ListTile(
                              leading: Icon(Icons.chat, color: Colors.deepPurple),
                              title: Text(
                                _geminiResponses[index],
                                style:
                                TextStyle(fontSize: 16, color: Colors.black87),
                              ),
                            ),
                          );
                        },
                      ),
                    ],
                  ),

                // Boutons Start et Stop
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 20),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      ElevatedButton.icon(
                        onPressed: _speechToText.isListening
                            ? null
                            : _startListening,
                        icon: Icon(Icons.mic),
                        label: Text("Start"),
                        style: ElevatedButton.styleFrom(
                          padding: EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 12,
                          ),
                          backgroundColor: Colors.green,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12.0),
                          ),
                        ),
                      ),
                      ElevatedButton.icon(
                        onPressed: _speechToText.isListening
                            ? _stopListening
                            : null,
                        icon: Icon(Icons.stop),
                        label: Text("Stop"),
                        style: ElevatedButton.styleFrom(
                          padding: EdgeInsets.symmetric(
                            horizontal: 24,
                            vertical: 12,
                          ),
                          backgroundColor: Colors.red,
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(12.0),
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
    );
  }}