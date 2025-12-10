
import tensorflow as tf
from tensorflow.keras import layers
import os

print("="*70)
print("ENTRAINEMENT AVEC TRANSFER LEARNING")
print("="*70)

IMG_SIZE = (224, 224)
BATCH_SIZE = 16  # Réduit pour petit dataset
EPOCHS = 30  # Plus d'époques
CLASSES = ['apple', 'banana', 'carrot', 'orange', 'tomato']

def load_data():
    """Charge les données avec augmentation agressive"""
    print("\nChargement des données avec augmentation...")

    # Augmentation de données très agressive
    train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
        rescale=1./255,
        rotation_range=40,
        width_shift_range=0.3,
        height_shift_range=0.3,
        shear_range=0.3,
        zoom_range=0.3,
        horizontal_flip=True,
        vertical_flip=True,
        brightness_range=[0.7, 1.3],
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

    print(f"{train_generator.samples} images entrainement")
    print(f"{val_generator.samples} images validation")

    return train_generator, val_generator

def create_transfer_learning_model():
    """Crée un modèle avec MobileNetV2 pré-entraîné"""
    print("\nCréation du modèle Transfer Learning...")

    # Charger MobileNetV2 pré-entraîné sur ImageNet
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(*IMG_SIZE, 3),
        include_top=False,
        weights='imagenet'
    )

    # Geler le modèle de base
    base_model.trainable = False

    # Construire le modèle complet
    model = tf.keras.Sequential([
        layers.Input(shape=(*IMG_SIZE, 3)),
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dropout(0.5),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        layers.Dense(len(CLASSES), activation='softmax')
    ])

    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    return model, base_model

def fine_tune_model(model, base_model, train_gen, val_gen):
    """Fine-tuning : débloquer les dernières couches"""
    print("\nFine-tuning du modèle...")

    # Débloquer les 50 dernières couches de MobileNetV2
    base_model.trainable = True
    for layer in base_model.layers[:-50]:
        layer.trainable = False

    # Recompiler avec un learning rate plus faible
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=0.0001),
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )

    # Callbacks
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

    # Entraîner
    history = model.fit(
        train_gen,
        epochs=EPOCHS,
        validation_data=val_gen,
        callbacks=callbacks,
        verbose=1
    )

    return history

def main():
    """Fonction principale"""
    try:
        os.makedirs('models', exist_ok=True)

        # Charger les données
        train_gen, val_gen = load_data()

        # Phase 1 : Entraînement initial
        print("\n" + "="*70)
        print("PHASE 1 : ENTRAINEMENT INITIAL")
        print("="*70)

        model, base_model = create_transfer_learning_model()

        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_accuracy',
                patience=8,
                restore_best_weights=True
            )
        ]

        history1 = model.fit(
            train_gen,
            epochs=20,
            validation_data=val_gen,
            callbacks=callbacks,
            verbose=1
        )

        # Phase 2 : Fine-tuning
        print("\n" + "="*70)
        print("PHASE 2 : FINE-TUNING")
        print("="*70)

        history2 = fine_tune_model(model, base_model, train_gen, val_gen)

        # Sauvegarder
        model.save('models/cnn_model.h5')

        # Évaluation finale
        print("\n" + "="*70)
        print("EVALUATION FINALE")
        print("="*70)

        val_loss, val_acc = model.evaluate(val_gen, verbose=0)

        print(f"\nPrécision finale : {val_acc*100:.2f}%")
        print(f"Loss : {val_loss:.4f}")
        print(f"\nModèle sauvegardé : models/cnn_model.h5")

        # Créer aussi une version ANN simple
        print("\n" + "="*70)
        print("CREATION DU MODELE ANN")
        print("="*70)

        ann_model = tf.keras.Sequential([
            layers.Input(shape=(*IMG_SIZE, 3)),
            layers.Flatten(),
            layers.Dense(512, activation='relu'),
            layers.Dropout(0.3),  # Réduit de 0.6 à 0.3
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),  # Réduit de 0.5 à 0.3
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.2),  # Réduit de 0.4 à 0.2
            layers.Dense(len(CLASSES), activation='softmax')
        ])

        ann_model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.0005),
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )

        ann_history = ann_model.fit(
            train_gen,
            epochs=30,
            validation_data=val_gen,
            callbacks=callbacks,
            verbose=1
        )

        ann_model.save('models/ann_model.h5')
        ann_loss, ann_acc = ann_model.evaluate(val_gen, verbose=0)

        print(f"\nANN Précision : {ann_acc*100:.2f}%")
        print(f"\nModèles sauvegardés avec succès")
        print("Lancez : python app.py")

    except KeyboardInterrupt:
        print("\n\nEntraînement interrompu")
    except Exception as e:
        print(f"\n\nErreur : {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()