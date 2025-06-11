from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import numpy as np
from typing import List
import cv2
from app.ocr.processor import ReceiptOCR # Import class OCR 
from model.model import load_model_assets, find_recipes
import tensorflow as tf

app = FastAPI()

# === Load model sekali saja saat startup ===
model_path = "model/recipe_model.pkl"
model, recipe_titles, ingredient_list = load_model_assets(model_path)

# Buat binary matrix sekali (untuk find_recipes)
import pandas as pd
df = pd.read_csv('./data/processed/resep_tfidf_features.csv')
X_features_df = df.iloc[:, 1:]
recipe_matrix_binary = tf.constant(X_features_df.values > 0, dtype=tf.bool)

# Tambah ke fungsi agar bisa diakses
find_recipes_globals = {
    "recipe_matrix_binary": recipe_matrix_binary,
    "recipe_titles": recipe_titles,
    "ingredient_list": ingredient_list
}

# Request body schema 
class IngredientsRequest(BaseModel):
    ingredients: list[str]

@app.get("/")
def home():
    return {"message": "API is running!"}

@app.post("/predict")
def predict_recipe(req: IngredientsRequest):
    response = find_recipes(
        ingredients_input=req.ingredients,
        num_recommendations=5,
        min_score_threshold=0.1,
        **find_recipes_globals  # Inject variabel global
    )
    return response

@app.post("/ocr")
async def recommend_from_receipt(image: UploadFile = File(...)):
    try:
        # 1. Baca gambar
        contents = await image.read()
        np_img = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        # 2. OCR + pencocokan produk
        ocr = ReceiptOCR(img, products_file='data/raw/product.txt')
        parsed = ocr.parse_receipt()

        categories = []
        for item in parsed['items']:
            match = ocr.find_closest_product(item['nama'])
            if match['kategori'] != 'Tidak Diketahui':
                categories.append(match['kategori'])

        # Hilangkan duplikat sambil mempertahankan urutan
        unique_categories = list(dict.fromkeys(categories))

        if not unique_categories:
            return JSONResponse(
                status_code=400,
                content={"error": "Tidak ada kategori produk yang terdeteksi dari struk."}
            )

        # 3. Prediksi resep dari kategori
        response = find_recipes(
            ingredients_input=unique_categories,
            num_recommendations=5,
            min_score_threshold=0.1,
            **find_recipes_globals  # variabel global seperti vectorizer, matrix, dll
        )

        return {
            "ingredients": unique_categories,
            "recommendations": response
        }

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
