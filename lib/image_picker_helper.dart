import 'dart:html' as html;
import 'dart:typed_data';
import 'dart:async';

class ImagePickerHelper {
  /// Ouvre le sélecteur de fichiers et retourne l'image en tant que [Uint8List] et [String] pour l'URL.
  static Future<Map<String, dynamic>> pickImage() async {
    final html.FileUploadInputElement uploadInput = html.FileUploadInputElement();
    uploadInput.accept = 'image/*'; // Accepte uniquement les fichiers image
    uploadInput.click();

    final completer = Completer<Map<String, dynamic>>();
    uploadInput.onChange.listen((event) {
      final file = uploadInput.files!.first;
      final reader = html.FileReader();

      reader.readAsDataUrl(file); // Lit le fichier pour l'afficher
      reader.onLoadEnd.listen((_) {
        completer.complete({
          "file": file,
          "imageUrl": reader.result as String,
        });
      });
    });

    return completer.future;
  }
}