# Import de TensorFlow, la bibliothèque principale pour le deep learning
# TensorFlow va gérer toute la création et l'entraînement des réseaux de neurones
import tensorflow as tf
from tensorflow.keras import layers  # Les "briques" pour construire nos réseaux
import numpy as np  # Pour les opérations mathématiques sur les tableaux
import os  # Pour interagir avec le système de fichiers

# Affichage d'un en-tête visuel pour marquer le début du processus
print("="*70)
print("ENTRAINEMENT DES MODELES CNN ET ANN")
print("="*70)

# Configuration globale : ces constantes seront utilisées partout dans le code
# IMG_SIZE définit la taille à laquelle toutes les images seront redimensionnées
# 224x224 est un standard car c'est la taille d'entrée de beaucoup de modèles pré-entraînés
IMG_SIZE = (224, 224)

# BATCH_SIZE = 16 signifie qu'on entraîne sur 16 images à la fois
# Un batch plus petit (comme 16 au lieu de 32) consomme moins de mémoire mais l'entraînement est plus lent
# C'est un compromis entre vitesse et stabilité de l'entraînement
BATCH_SIZE = 16  # Réduit

# EPOCHS = 30 signifie que le modèle va voir l'ensemble complet des données 30 fois
# Plus d'époques permettent un meilleur apprentissage, mais risquent l'overfitting si trop élevé
EPOCHS = 30  # Augmenté

# Les 5 classes que notre modèle doit apprendre à distinguer
# L'ordre est important car il détermine les indices : apple=0, banana=1, carrot=2, etc.
CLASSES = ['apple', 'banana', 'carrot', 'orange', 'tomato']

def check_dataset():
    """
    Cette fonction vérifie que le dataset existe et contient suffisamment d'images
    pour l'entraînement. C'est une étape de sécurité cruciale avant de commencer.

    Structure attendue du dataset :
    data/
      train/
        apple/ (contient des images de pommes)
        banana/
        carrot/
        orange/
        tomato/
      validation/
        apple/
        banana/
        etc.
    """
    print("\nVerification du dataset...")

    # Compteurs pour garder trace du nombre total d'images
    total_train = 0
    total_val = 0

    # Pour chaque classe de fruits/légumes que nous voulons reconnaître
    for cls in CLASSES:
        # Construire les chemins vers les dossiers de train et validation
        # f-string permet d'insérer la variable cls dans le chemin
        train_path = f'data/train/{cls}'
        val_path = f'data/validation/{cls}'

        # Compter le nombre de fichiers image dans chaque dossier
        # os.listdir() liste tous les fichiers, on filtre pour garder uniquement les images
        # La compréhension de liste avec if filtre les fichiers par extension
        # Le 'if os.path.exists()' évite une erreur si le dossier n'existe pas
        train_images = len([f for f in os.listdir(train_path) if f.endswith(('.jpg', '.jpeg', '.png'))]) if os.path.exists(train_path) else 0
        val_images = len([f for f in os.listdir(val_path) if f.endswith(('.jpg', '.jpeg', '.png'))]) if os.path.exists(val_path) else 0

        # Accumuler dans les totaux
        total_train += train_images
        total_val += val_images

        # Afficher le compte pour cette classe spécifique
        # Cela permet de détecter rapidement si une classe manque d'images
        print(f"  {cls}: {train_images} train, {val_images} validation")

    # Afficher le total global pour avoir une vue d'ensemble
    print(f"\nTotal : {total_train} images entrainement, {total_val} validation")

    # Vérification de sécurité : si moins de 50 images au total, l'entraînement sera inefficace
    # Un réseau de neurones a besoin d'assez d'exemples pour apprendre des patterns généraux
    if total_train < 50:
        print("\nDataset insuffisant. Ajoutez plus d'images dans data/train/ et data/validation/")
        return False  # Retourne False pour signaler un problème

    return True  # Retourne True si tout est OK

def load_data():
    """
    Charge et prépare les données d'entraînement et de validation.

    Cette fonction fait deux choses cruciales :
    1. Augmentation de données (data augmentation) pour l'entraînement
    2. Normalisation pour que les pixels soient entre 0 et 1

    L'augmentation de données est une technique qui génère artificiellement de nouvelles
    images en appliquant des transformations aléatoires (rotation, zoom, etc.) aux images
    existantes. Cela permet d'avoir un dataset virtuel beaucoup plus grand, ce qui aide
    à éviter l'overfitting et améliore la généralisation.
    """
    print("\nChargement des donnees...")

    # ImageDataGenerator pour l'ENTRAÎNEMENT avec augmentation de données agressive
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        # rescale=1./255 convertit les pixels de [0-255] à [0-1]
        # Les réseaux de neurones apprennent mieux avec des valeurs normalisées
        rescale=1./255,

        # rotation_range=40 fait pivoter l'image aléatoirement jusqu'à ±40 degrés
        # Une pomme reste une pomme même si elle est légèrement tournée
        rotation_range=40,  # Augmenté

        # width_shift_range=0.3 déplace l'image horizontalement jusqu'à 30% de sa largeur
        # Cela simule une photo prise légèrement décentrée
        width_shift_range=0.3,  # Augmenté

        # height_shift_range=0.3 déplace l'image verticalement
        height_shift_range=0.3,  # Augmenté

        # shear_range=0.3 applique une transformation de cisaillement
        # C'est comme si tu regardais l'objet sous un angle oblique
        shear_range=0.3,  # Ajouté

        # zoom_range=0.3 fait un zoom avant ou arrière aléatoire
        # Simule des photos prises à différentes distances
        zoom_range=0.3,  # Augmenté

        # horizontal_flip=True retourne l'image horizontalement (effet miroir)
        # Une banane reste une banane même en miroir
        horizontal_flip=True,

        # vertical_flip=True retourne l'image verticalement
        # Attention : pour certains objets cela pourrait être problématique
        vertical_flip=True,  # Ajouté

        # brightness_range varie la luminosité de l'image
        # Simule différentes conditions d'éclairage
        brightness_range=[0.7, 1.3],  # Ajouté

        # fill_mode='nearest' définit comment remplir les pixels créés par les transformations
        # 'nearest' copie les pixels les plus proches
        fill_mode='nearest'
    )

    # ImageDataGenerator pour la VALIDATION sans augmentation
    # Pourquoi pas d'augmentation ? Parce que nous voulons évaluer le modèle sur des images
    # "normales" pour savoir comment il performera en conditions réelles
    val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255  # Uniquement la normalisation, pas de transformations
    )

    # flow_from_directory charge les images depuis une structure de dossiers
    # Il parcourt automatiquement les sous-dossiers et attribue les labels
    train_generator = train_datagen.flow_from_directory(
        'data/train',  # Chemin du dossier contenant les sous-dossiers de classes
        target_size=IMG_SIZE,  # Redimensionne toutes les images à 224x224
        batch_size=BATCH_SIZE,  # Retourne 16 images à la fois
        class_mode='sparse',  # 'sparse' signifie que les labels sont des entiers (0,1,2,3,4)
        classes=CLASSES,  # Force l'ordre des classes pour être cohérent
        shuffle=True  # Mélange les images à chaque époque pour éviter les biais d'ordre
    )

    # Même chose pour la validation, mais sans mélange
    # On ne mélange pas la validation car l'ordre n'affecte pas l'évaluation
    val_generator = val_datagen.flow_from_directory(
        'data/validation',
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='sparse',
        classes=CLASSES,
        shuffle=False  # Pas de mélange pour la validation
    )

    # Affiche le nombre d'images trouvées pour vérifier que tout va bien
    print(f"{train_generator.samples} images entrainement chargees")
    print(f"{val_generator.samples} images validation chargees")

    return train_generator, val_generator

def create_cnn_model():
    """
    Crée l'architecture du Convolutional Neural Network (CNN).


    Un CNN est spécialement conçu pour les images. Il utilise des convolutions pour
    détecter progressivement des features de plus en plus complexes :
    - Les premières couches détectent des bords et des coins
    - Les couches intermédiaires détectent des textures et des patterns
    - Les dernières couches détectent des formes complètes et des objets

    L'architecture suit un pattern classique : Conv → Conv → Pool → Dropout
    Ce pattern est répété 3 fois avec des filtres de plus en plus nombreux.
    """
    print("\nCreation du modele CNN...")

    # Sequential signifie que les couches sont empilées les unes après les autres
    # C'est le type de modèle le plus simple et le plus courant
    model = tf.keras.Sequential([
        # Input définit la forme des données en entrée : (224, 224, 3)
        # 224x224 pixels avec 3 canaux de couleur (Rouge, Vert, Bleu)
        layers.Input(shape=(*IMG_SIZE, 3)),

        # BLOC 1 : Détection de features basiques
        # Conv2D(32, (3,3)) crée 32 filtres de taille 3x3 pixels
        # Chaque filtre apprend à détecter un pattern différent (bord vertical, horizontal, etc.)
        # padding='same' ajoute des zéros autour pour garder la même taille d'image
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),

        # BatchNormalization normalise les activations entre couches
        # Cela accélère l'entraînement et stabilise l'apprentissage
        layers.BatchNormalization(),

        # Deuxième convolution pour renforcer la détection
        # Deux convolutions successives peuvent détecter des patterns plus complexes
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),

        # MaxPooling(2,2) réduit la taille de moitié en gardant les valeurs maximales
        # 224x224 → 112x112
        # Cela réduit le nombre de paramètres et crée une invariance à la position
        layers.MaxPooling2D((2, 2)),

        # Dropout(0.25) désactive aléatoirement 25% des neurones pendant l'entraînement
        # C'est une technique de régularisation qui évite l'overfitting
        layers.Dropout(0.25),

        # BLOC 2 : Détection de features intermédiaires (textures)
        # On double le nombre de filtres (32 → 64) car l'image est plus petite
        # Plus l'image est petite, plus on peut avoir de filtres sans exploser la mémoire
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),  # 112x112 → 56x56
        layers.Dropout(0.25),

        # BLOC 3 : Détection de features complexes (formes, objets partiels)
        # Encore doublement des filtres (64 → 128)
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),  # 56x56 → 28x28
        layers.Dropout(0.25),

        # PARTIE CLASSIFICATION
        # Flatten transforme la carte de features 3D (28x28x128) en vecteur 1D
        # Nécessaire car les couches Dense n'acceptent que des vecteurs
        layers.Flatten(),

        # Dense(256) : Couche fully-connected avec 256 neurones
        # Cette couche apprend à combiner les features détectées pour la classification
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),  # Dropout plus élevé (50%) car cette couche a beaucoup de paramètres

        # Dense(128) : Couche intermédiaire de décision
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),

        # Dense(5) avec softmax : Couche de sortie finale
        # 5 neurones, un par classe
        # softmax transforme les scores en probabilités qui s'additionnent à 1
        layers.Dense(len(CLASSES), activation='softmax')
    ])

    # Compilation du modèle : on définit comment il va apprendre
    model.compile(
        # Adam est un optimiseur qui ajuste les poids du réseau
        # learning_rate=0.001 contrôle la taille des "pas" lors de l'apprentissage
        # Un learning rate trop élevé rend l'apprentissage instable
        # Un learning rate trop faible rend l'apprentissage très lent
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),

        # sparse_categorical_crossentropy est la fonction de perte pour la classification
        # Elle mesure l'écart entre les prédictions et les vraies classes
        # 'sparse' car nos labels sont des entiers (0,1,2,3,4) et non des vecteurs one-hot
        loss='sparse_categorical_crossentropy',

        # accuracy : métrique pour suivre le pourcentage de prédictions correctes
        metrics=['accuracy']
    )

    return model

def train_cnn(train_gen, val_gen):
    """
    Entraîne le modèle CNN sur les données fournies.

    L'entraînement est un processus itératif :
    1. Le modèle fait des prédictions sur un batch d'images
    2. On calcule l'erreur (loss) entre les prédictions et les vraies classes
    3. On ajuste les poids du réseau pour réduire cette erreur
    4. On répète pour tous les batchs, c'est une époque
    5. On répète les époques jusqu'à convergence
    """
    print("\n" + "="*70)
    print("ENTRAINEMENT DU MODELE CNN")
    print("="*70)
    print(f"Temps estime : 15-30 minutes")
    print(f"{EPOCHS} epoques d'entrainement\n")

    # Créer le modèle CNN avec l'architecture définie précédemment
    model = create_cnn_model()

    # Callbacks : fonctions appelées automatiquement pendant l'entraînement
    # Elles permettent de contrôler le processus d'entraînement de manière intelligente
    callbacks = [
        # EarlyStopping arrête l'entraînement si la validation n'améliore plus
        # Cela évite de perdre du temps et de faire de l'overfitting
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy',  # On surveille la précision sur les données de validation
            patience=10,  # On attend 10 époques sans amélioration avant d'arrêter
            restore_best_weights=True  # On garde les meilleurs poids, pas les derniers
        ),

        # ReduceLROnPlateau réduit le learning rate quand on stagne
        # Quand l'apprentissage ralentit, un learning rate plus petit peut aider à affiner
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',  # On surveille la perte sur la validation
            factor=0.5,  # On divise le learning rate par 2 quand on stagne
            patience=5,  # On attend 5 époques de stagnation avant de réduire
            min_lr=0.00001  # On ne descend pas en dessous de ce seuil
        )
    ]

    # Lancement de l'entraînement
    # fit() est la méthode qui fait tout le travail
    history = model.fit(
        train_gen,  # Générateur qui fournit les batchs d'entraînement
        epochs=EPOCHS,  # Nombre maximum d'époques (peut s'arrêter avant avec EarlyStopping)
        validation_data=val_gen,  # Données pour évaluer le modèle à chaque époque
        callbacks=callbacks,  # Les callbacks définis ci-dessus
        verbose=1  # Affiche une barre de progression pour chaque époque
    )

    # Sauvegarde du modèle entraîné sur le disque
    # Le format .h5 stocke l'architecture ET tous les poids appris
    model.save('models/cnn_model.h5')

    # Récupération des métriques finales pour affichage
    # history.history est un dictionnaire contenant toutes les métriques de chaque époque
    final_train_acc = history.history['accuracy'][-1]  # [-1] prend la dernière valeur
    final_val_acc = history.history['val_accuracy'][-1]

    # Affichage des résultats finaux
    print("\n" + "="*70)
    print("MODELE CNN ENTRAINE ET SAUVEGARDE")
    print("="*70)
    print(f"Precision entrainement : {final_train_acc*100:.2f}%")
    print(f"Precision validation : {final_val_acc*100:.2f}%")
    print(f"Sauvegarde : models/cnn_model.h5")

    return model, history

def create_ann_model():
    """
    Crée l'architecture du Artificial Neural Network (ANN).

    Un ANN simple (aussi appelé MLP - Multi-Layer Perceptron) traite les images comme
    des vecteurs plats. Il ne comprend pas la structure spatiale des images.

    Contrairement au CNN qui préserve les relations spatiales avec des convolutions,
    l'ANN aplatit tout en un long vecteur et utilise uniquement des couches denses.

    C'est pourquoi les ANN sont généralement moins performants que les CNN sur les images :
    ils perdent l'information cruciale sur quels pixels sont voisins.
    """
    print("\nCreation du modele ANN...")

    model = tf.keras.Sequential([
        # Input : même taille qu'un CNN (224, 224, 3)
        layers.Input(shape=(*IMG_SIZE, 3)),

        # FLATTEN : C'EST LA DIFFÉRENCE CRUCIALE AVEC LE CNN
        # Cette couche transforme l'image 3D (224, 224, 3) en un vecteur 1D de 150528 valeurs
        # On perd complètement l'information spatiale : le réseau ne sait plus quels pixels
        # étaient voisins dans l'image originale
        layers.Flatten(),

        # Première couche dense : 150528 → 1024
        # ATTENTION : cela crée 150528 × 1024 = 154,140,672 connexions !
        # C'est énorme comparé aux filtres 3x3 du CNN
        # Chaque connexion a un poids à apprendre, d'où le risque d'overfitting
        layers.Dense(1024, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),  # Dropout élevé pour contrer l'overfitting

        # Couches suivantes : compression progressive de l'information
        # 1024 → 512 → 256 → 128 → 5
        # C'est un entonnoir qui force le réseau à extraire les features essentielles
        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),

        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),

        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),

        # Couche de sortie : identique au CNN
        # 5 neurones avec softmax pour les probabilités de chaque classe
        layers.Dense(len(CLASSES), activation='softmax')
    ])

    # Compilation identique au CNN pour une comparaison équitable
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def train_ann(train_gen, val_gen):
    """
    Entraîne le modèle ANN.

    Le processus est identique à celui du CNN, seule l'architecture interne diffère.
    On utilise les mêmes callbacks et hyperparamètres pour une comparaison juste.
    """
    print("\n" + "="*70)
    print("ENTRAINEMENT DU MODELE ANN")
    print("="*70)
    print(f"Temps estime : 10-20 minutes")
    print(f"{EPOCHS} epoques d'entrainement\n")

    model = create_ann_model()

    # Callbacks identiques au CNN
    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=10,
            restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,
            min_lr=0.00001
        )
    ]

    # Entraînement
    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )

    # Sauvegarde du modèle ANN
    model.save('models/ann_model.h5')

    # Récupération et affichage des résultats
    final_train_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]

    print("\n" + "="*70)
    print("MODELE ANN ENTRAINE ET SAUVEGARDE")
    print("="*70)
    print(f"Precision entrainement : {final_train_acc*100:.2f}%")
    print(f"Precision validation : {final_val_acc*100:.2f}%")
    print(f"Sauvegarde : models/ann_model.h5")

    return model, history

def evaluate_models(cnn_model, ann_model, val_gen):
    """
    Compare les performances des deux modèles sur les mêmes données de validation.

    Cette comparaison est cruciale pour comprendre l'importance de l'architecture.
    Même avec les mêmes données et hyperparamètres, le CNN devrait largement
    surpasser l'ANN car il est mieux adapté aux images.
    """
    print("\n" + "="*70)
    print("EVALUATION ET COMPARAISON")
    print("="*70)

    # evaluate() calcule la perte et l'accuracy sur l'ensemble de validation complet
    print("\nEvaluation du modele CNN...")
    cnn_loss, cnn_acc = cnn_model.evaluate(val_gen, verbose=0)

    print("Evaluation du modele ANN...")
    ann_loss, ann_acc = ann_model.evaluate(val_gen, verbose=0)

    # Affichage des résultats côte à côte pour une comparaison facile
    print("\n" + "="*70)
    print("RESULTATS FINAUX")
    print("="*70)
    print(f"\nCNN Model:")
    print(f"   Precision : {cnn_acc*100:.2f}%")
    print(f"   Loss : {cnn_loss:.4f}")

    print(f"\nANN Model:")
    print(f"   Precision : {ann_acc*100:.2f}%")
    print(f"   Loss : {ann_loss:.4f}")

    # Calcul et affichage de la différence de performance
    # Cette différence illustre l'importance d'utiliser l'architecture appropriée
    if cnn_acc > ann_acc:
        print(f"\nLe modele CNN est meilleur (+{(cnn_acc-ann_acc)*100:.2f}%)")
    else:
        print(f"\nLe modele ANN est meilleur (+{(ann_acc-cnn_acc)*100:.2f}%)")

    # Instructions pour la suite
    print("\n" + "="*70)
    print("ENTRAINEMENT TERMINE")
    print("="*70)
    print("\nModeles sauvegardes :")
    print("   - models/cnn_model.h5")
    print("   - models/ann_model.h5")
    print("\nLancez le serveur :")
    print("   python app_final.py")

def main():
    """
    Fonction principale qui orchestre tout le processus d'entraînement.

    Le workflow complet est :
    1. Vérifier que le dataset existe et est suffisant
    2. Charger et préparer les données
    3. Entraîner le CNN
    4. Entraîner l'ANN
    5. Comparer les deux modèles

    Les try/except permettent de gérer proprement les interruptions et les erreurs.
    """
    try:
        # Créer le dossier models s'il n'existe pas
        # exist_ok=True évite une erreur si le dossier existe déjà
        os.makedirs('models', exist_ok=True)

        # Vérification du dataset : on arrête tout si insuffisant
        if not check_dataset():
            return

        # Chargement des données avec augmentation
        train_gen, val_gen = load_data()

        # Entraînement séquentiel des deux modèles
        # On garde les objets history pour une analyse post-entraînement éventuelle
        cnn_model, cnn_history = train_cnn(train_gen, val_gen)
        ann_model, ann_history = train_ann(train_gen, val_gen)

        # Comparaison finale des performances
        evaluate_models(cnn_model, ann_model, val_gen)

    except KeyboardInterrupt:
        # Gestion propre de l'interruption par Ctrl+C
        print("\n\nEntrainement interrompu par utilisateur")
    except Exception as e:
        # Capture toute autre erreur et affiche la stack trace complète
        # Utile pour le débogage
        print(f"\n\nErreur : {e}")
        import traceback
        traceback.print_exc()

# Point d'entrée du script
# __name__ == "__main__" est True uniquement si le script est exécuté directement
# (pas importé comme module)
if __name__ == "__main__":
    main()