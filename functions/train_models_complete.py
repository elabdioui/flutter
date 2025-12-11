import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import os

print("="*70)
print("ENTRAINEMENT DES MODELES CNN ET ANN")
print("="*70)

# Configuration
IMG_SIZE = (224, 224)
BATCH_SIZE = 16  # Réduit
EPOCHS = 30  # Augmenté
CLASSES = ['apple', 'banana', 'carrot', 'orange', 'tomato']

def check_dataset():
    """Verifie si le dataset existe"""
    print("\nVerification du dataset...")

    total_train = 0
    total_val = 0

    for cls in CLASSES:
        train_path = f'data/train/{cls}'
        val_path = f'data/validation/{cls}'

        train_images = len([f for f in os.listdir(train_path) if f.endswith(('.jpg', '.jpeg', '.png'))]) if os.path.exists(train_path) else 0
        val_images = len([f for f in os.listdir(val_path) if f.endswith(('.jpg', '.jpeg', '.png'))]) if os.path.exists(val_path) else 0

        total_train += train_images
        total_val += val_images

        print(f"  {cls}: {train_images} train, {val_images} validation")

    print(f"\nTotal : {total_train} images entrainement, {total_val} validation")

    if total_train < 50:
        print("\nDataset insuffisant. Ajoutez plus d'images dans data/train/ et data/validation/")
        return False

    return True

def load_data():
    """Charge et prepare les donnees"""
    print("\nChargement des donnees...")

    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,  # Augmenté
        width_shift_range=0.3,  # Augmenté
        height_shift_range=0.3,  # Augmenté
        shear_range=0.3,  # Ajouté
        zoom_range=0.3,  # Augmenté
        horizontal_flip=True,
        vertical_flip=True,  # Ajouté
        brightness_range=[0.7, 1.3],  # Ajouté
        fill_mode='nearest'
    )

    val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255
    )

    train_generator = train_datagen.flow_from_directory(
        'data/train',
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='sparse',
        classes=CLASSES,
        shuffle=True
    )

    val_generator = val_datagen.flow_from_directory(
        'data/validation',
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='sparse',
        classes=CLASSES,
        shuffle=False
    )

    print(f"{train_generator.samples} images entrainement chargees")
    print(f"{val_generator.samples} images validation chargees")

    return train_generator, val_generator

def create_cnn_model():
    """Cree le modele CNN"""
    print("\nCreation du modele CNN...")

    model = tf.keras.Sequential([
        layers.Input(shape=(*IMG_SIZE, 3)),

        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.BatchNormalization(),
        layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
        layers.MaxPooling2D((2, 2)),
        layers.Dropout(0.25),

        layers.Flatten(),
        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),
        layers.Dense(len(CLASSES), activation='softmax')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def train_cnn(train_gen, val_gen):
    """Entraine le modele CNN"""
    print("\n" + "="*70)
    print("ENTRAINEMENT DU MODELE CNN")
    print("="*70)
    print(f"Temps estime : 15-30 minutes")
    print(f"{EPOCHS} epoques d'entrainement\n")

    model = create_cnn_model()

    callbacks = [
        tf.keras.callbacks.EarlyStopping(
            monitor='val_accuracy',
            patience=10,  # Augmenté de 5 à 10
            restore_best_weights=True
        ),
        tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=5,  # Augmenté de 3 à 5
            min_lr=0.00001
        )
    ]

    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )

    model.save('models/cnn_model.h5')

    final_train_acc = history.history['accuracy'][-1]
    final_val_acc = history.history['val_accuracy'][-1]

    print("\n" + "="*70)
    print("MODELE CNN ENTRAINE ET SAUVEGARDE")
    print("="*70)
    print(f"Precision entrainement : {final_train_acc*100:.2f}%")
    print(f"Precision validation : {final_val_acc*100:.2f}%")
    print(f"Sauvegarde : models/cnn_model.h5")

    return model, history

def create_ann_model():
    """Cree le modele ANN"""
    print("\nCreation du modele ANN...")

    model = tf.keras.Sequential([
        layers.Input(shape=(*IMG_SIZE, 3)),
        layers.Flatten(),

        layers.Dense(1024, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),

        layers.Dense(512, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),

        layers.Dense(256, activation='relu'),
        layers.BatchNormalization(),
        layers.Dropout(0.5),

        layers.Dense(128, activation='relu'),
        layers.Dropout(0.5),

        layers.Dense(len(CLASSES), activation='softmax')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model

def train_ann(train_gen, val_gen):
    """Entraine le modele ANN"""
    print("\n" + "="*70)
    print("ENTRAINEMENT DU MODELE ANN")
    print("="*70)
    print(f"Temps estime : 10-20 minutes")
    print(f"{EPOCHS} epoques d'entrainement\n")

    model = create_ann_model()

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

    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )

    model.save('models/ann_model.h5')

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
    """Compare les deux modeles"""
    print("\n" + "="*70)
    print("EVALUATION ET COMPARAISON")
    print("="*70)

    print("\nEvaluation du modele CNN...")
    cnn_loss, cnn_acc = cnn_model.evaluate(val_gen, verbose=0)

    print("Evaluation du modele ANN...")
    ann_loss, ann_acc = ann_model.evaluate(val_gen, verbose=0)

    print("\n" + "="*70)
    print("RESULTATS FINAUX")
    print("="*70)
    print(f"\nCNN Model:")
    print(f"   Precision : {cnn_acc*100:.2f}%")
    print(f"   Loss : {cnn_loss:.4f}")

    print(f"\nANN Model:")
    print(f"   Precision : {ann_acc*100:.2f}%")
    print(f"   Loss : {ann_loss:.4f}")

    if cnn_acc > ann_acc:
        print(f"\nLe modele CNN est meilleur (+{(cnn_acc-ann_acc)*100:.2f}%)")
    else:
        print(f"\nLe modele ANN est meilleur (+{(ann_acc-cnn_acc)*100:.2f}%)")

    print("\n" + "="*70)
    print("ENTRAINEMENT TERMINE")
    print("="*70)
    print("\nModeles sauvegardes :")
    print("   - models/cnn_model.h5")
    print("   - models/ann_model.h5")
    print("\nLancez le serveur :")
    print("   python app_final.py")

def main():
    """Fonction principale"""
    try:
        os.makedirs('models', exist_ok=True)

        if not check_dataset():
            return

        train_gen, val_gen = load_data()
        cnn_model, cnn_history = train_cnn(train_gen, val_gen)
        ann_model, ann_history = train_ann(train_gen, val_gen)
        evaluate_models(cnn_model, ann_model, val_gen)

    except KeyboardInterrupt:
        print("\n\nEntrainement interrompu par utilisateur")
    except Exception as e:
        print(f"\n\nErreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()