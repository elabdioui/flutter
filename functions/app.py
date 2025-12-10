from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import tensorflow as tf
import numpy as np
from PIL import Image
import io
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CLASSES = ['apple', 'banana', 'carrot', 'orange', 'tomato']
cnn_model = None
ann_model = None

def load_models():
    """Charge les modeles entraines"""
    global cnn_model, ann_model

    print("\n" + "="*60)
    print("Chargement des modeles...")
    print("="*60)

    cnn_path = 'models/cnn_model.h5'
    if os.path.exists(cnn_path):
        try:
            cnn_model = tf.keras.models.load_model(cnn_path)
            print(f"Modele CNN charge depuis {cnn_path}")
        except Exception as e:
            print(f"Erreur CNN : {e}")
    else:
        print(f"Modele CNN non trouve : {cnn_path}")

    ann_path = 'models/ann_model.h5'
    if os.path.exists(ann_path):
        try:
            ann_model = tf.keras.models.load_model(ann_path)
            print(f"Modele ANN charge depuis {ann_path}")
        except Exception as e:
            print(f"Erreur ANN : {e}")
    else:
        print(f"Modele ANN non trouve : {ann_path}")

    if not cnn_model and not ann_model:
        print("\nAucun modele entraine trouve")
        print("Executez : python train_models_complete.py")

    print("="*60)

def preprocess_image(image_bytes, target_size=(224, 224)):
    """Pretraite l'image pour la prediction"""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert('RGB')
    img = img.resize(target_size)

    x = np.array(img, dtype=np.float32) / 255.0
    x = np.expand_dims(x, axis=0)

    return x

def predict_with_model(image_bytes, model, model_name):
    """Fait une prediction avec un modele"""
    try:
        x = preprocess_image(image_bytes)
        predictions = model.predict(x, verbose=0)

        idx = np.argmax(predictions[0])
        confidence = float(predictions[0][idx] * 100)
        label = CLASSES[idx]

        all_probs = {
            CLASSES[i]: float(predictions[0][i] * 100)
            for i in range(len(CLASSES))
        }

        return {
            "label": label,
            "confidence": f"{confidence:.2f}%",
            "model": model_name,
            "all_predictions": all_probs
        }

    except Exception as e:
        return {
            "error": str(e),
            "model": model_name
        }

def smart_color_prediction(image_bytes):
    """Prediction de secours basee sur les couleurs"""
    img = Image.open(io.BytesIO(image_bytes))
    img = img.convert('RGB')
    img_small = img.resize((50, 50))
    pixels = np.array(img_small)

    avg_color = pixels.mean(axis=(0, 1))
    r, g, b = avg_color

    scores = {
        'tomato': 0,
        'apple': 0,
        'banana': 0,
        'carrot': 0,
        'orange': 0
    }

    if r > 150 and g < 100 and b < 100:
        scores['tomato'] = 80 + (r - g) / 10

    if (r > 150 and g < 120) or (g > r and g > 100):
        scores['apple'] = 75 + abs(r - g) / 10

    if r > 180 and g > 150 and b < 120:
        scores['banana'] = 85

    if r > 150 and 80 < g < 140 and b < 100:
        scores['carrot'] = 70

    if r > 180 and g > 120 and b < 100:
        scores['orange'] = 75

    predicted = max(scores, key=scores.get)
    confidence = min(scores[predicted], 85.0)

    return {
        "label": predicted,
        "confidence": f"{confidence:.2f}%",
        "model": "Detection couleur (fallback)",
        "all_predictions": scores
    }

@app.on_event("startup")
async def startup():
    """Charge les modeles au demarrage"""
    load_models()

@app.get("/")
def root():
    """Page d'accueil"""
    status = []

    if cnn_model:
        status.append("CNN OK")
    else:
        status.append("CNN manquant")

    if ann_model:
        status.append("ANN OK")
    else:
        status.append("ANN manquant")

    return {
        "message": "Serveur de classification actif",
        "models_status": " | ".join(status),
        "classes": CLASSES,
        "endpoints": {
            "predict": "/predict (utilise le meilleur modele)",
            "predict_cnn": "/predict/cnn",
            "predict_ann": "/predict/ann",
            "compare": "/compare (compare les deux modeles)"
        }
    }

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    """Prediction avec le meilleur modele disponible"""
    try:
        image_bytes = await file.read()

        if cnn_model:
            result = predict_with_model(image_bytes, cnn_model, "CNN")
        elif ann_model:
            result = predict_with_model(image_bytes, ann_model, "ANN")
        else:
            result = smart_color_prediction(image_bytes)

        return {"prediction": result}

    except Exception as e:
        return {"error": str(e)}

@app.post("/predict/cnn")
async def predict_cnn(file: UploadFile = File(...)):
    """Prediction avec le modele CNN"""
    try:
        image_bytes = await file.read()

        if cnn_model:
            result = predict_with_model(image_bytes, cnn_model, "CNN")
        else:
            result = {
                "error": "Modele CNN non disponible",
                "suggestion": "Executez : python train_models_complete.py"
            }

        return {"prediction": result}

    except Exception as e:
        return {"error": str(e)}

@app.post("/predict/ann")
async def predict_ann(file: UploadFile = File(...)):
    """Prediction avec le modele ANN"""
    try:
        image_bytes = await file.read()

        if ann_model:
            result = predict_with_model(image_bytes, ann_model, "ANN")
        else:
            result = {
                "error": "Modele ANN non disponible",
                "suggestion": "Executez : python train_models_complete.py"
            }

        return {"prediction": result}

    except Exception as e:
        return {"error": str(e)}

@app.post("/compare")
async def compare_models(file: UploadFile = File(...)):
    """Compare les predictions des deux modeles"""
    try:
        image_bytes = await file.read()

        results = {}

        if cnn_model:
            results["cnn"] = predict_with_model(image_bytes, cnn_model, "CNN")

        if ann_model:
            results["ann"] = predict_with_model(image_bytes, ann_model, "ANN")

        if not results:
            results["fallback"] = smart_color_prediction(image_bytes)

        return {"comparison": results}

    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
def health():
    """Verification de sante"""
    return {
        "status": "healthy",
        "cnn_loaded": cnn_model is not None,
        "ann_loaded": ann_model is not None
    }

@app.get("/models/info")
def models_info():
    """Informations sur les modeles"""
    info = {
        "classes": CLASSES,
        "num_classes": len(CLASSES)
    }

    if cnn_model:
        info["cnn"] = {
            "loaded": True,
            "input_shape": str(cnn_model.input_shape),
            "total_params": cnn_model.count_params()
        }
    else:
        info["cnn"] = {"loaded": False}

    if ann_model:
        info["ann"] = {
            "loaded": True,
            "input_shape": str(ann_model.input_shape),
            "total_params": ann_model.count_params()
        }
    else:
        info["ann"] = {"loaded": False}

    return info

if __name__ == "__main__":
    import uvicorn

    print("\n" + "="*60)
    print("Serveur de classification de fruits et legumes")
    print("="*60)
    print("URL : http://127.0.0.1:8000")
    print("Documentation : http://127.0.0.1:8000/docs")
    print("Infos modeles : http://127.0.0.1:8000/models/info")
    print("="*60 + "\n")

    uvicorn.run(app, host="127.0.0.1", port=8000)