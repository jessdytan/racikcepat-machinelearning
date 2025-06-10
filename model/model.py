import re
import pickle
import numpy as np
import tensorflow as tf
from keras.saving import register_keras_serializable

@register_keras_serializable()
class RecipeClassifier(tf.keras.Model):
    def __init__(self, num_recipes: int):
        super().__init__()
        self.dense1 = tf.keras.layers.Dense(256, activation='relu')
        self.dense2 = tf.keras.layers.Dense(128, activation='relu')
        self.output_layer = tf.keras.layers.Dense(num_recipes, activation='softmax')
        
    def call(self, inputs):
        x = self.dense1(inputs)
        x = self.dense2(x)
        return self.output_layer(x)

def tokenize_ingredients(ingredients_input: list[str]) -> list[str]:
    tokenized_input = []
    for item in ingredients_input:
        tokenized_input.extend(re.split(r'\s+', str(item).lower()))
    return tokenized_input

def find_recipe_final(
    ingredients_input: list[str],
    titles: list[str],
    ingredients: list[str],
    matrix_binary: tf.Tensor,
    verbose: bool = True
) -> str:
    if verbose:
        print(f"\n--- MENCARI RESEP UNTUK: {ingredients_input} ---")

    tokenized_input = tokenize_ingredients(ingredients_input)
    input_mask_np = np.isin(ingredients, tokenized_input)

    if not np.any(input_mask_np):
        return "NO_MATCH_INGREDIENTS"

    if verbose:
        print(f"Bahan dikenali: {[ing for ing in tokenized_input if ing in ingredients]}")

    input_mask = tf.constant(input_mask_np, dtype=tf.bool)

    missing_ingredients_mask = tf.logical_and(tf.logical_not(matrix_binary), input_mask)
    missing_count_per_recipe = tf.reduce_sum(tf.cast(missing_ingredients_mask, tf.int32), axis=1)
    passing_recipes_mask = tf.equal(missing_count_per_recipe, 0)

    if not tf.reduce_any(passing_recipes_mask):
        return "NO_MATCH_RECIPE"

    intersection = tf.reduce_sum(tf.cast(tf.logical_and(matrix_binary, input_mask), tf.float32), axis=1)
    total_ingredients_in_recipe = tf.reduce_sum(tf.cast(matrix_binary, tf.float32), axis=1)
    efficiency_score = intersection / (total_ingredients_in_recipe + 1e-6)

    final_scores = tf.where(passing_recipes_mask, efficiency_score, 0.0)

    best_recipe_index = tf.argmax(final_scores).numpy()
    best_score = final_scores[best_recipe_index].numpy()

    if best_score <= 0:
        return "NO_MATCH_SCORE"

    matched_recipe_name = titles[best_recipe_index]

    return (
        f"Resep yang paling sesuai adalah: **{matched_recipe_name}** (Skor Kecocokan: {best_score:.2f})"
        if verbose else matched_recipe_name
    )

def tokenize_ingredients(ingredients: list[str]) -> list[str]:
    tokens = []
    for item in ingredients:
        tokens.extend(re.split(r"\s+", item.lower()))
    return tokens

def find_recipes(
    ingredients_input: list[str],
    ingredient_list: list[str],
    recipe_matrix_binary: tf.Tensor,
    recipe_titles: list[str],
    num_recommendations: int = 5,
    min_score_threshold: float = 0.1
) -> dict:
    # Tokenisasi bahan
    tokenized_input = tokenize_ingredients(ingredients_input)

    # Cek kecocokan dengan ingredient_list
    input_mask_np = np.isin(ingredient_list, tokenized_input)
    recognized_ingredients = [ing for ing in tokenized_input if ing in ingredient_list]

    if not recognized_ingredients:
        return {
            "recommendations": [],
            "message": "Tidak ada bahan yang dikenali dalam sistem kami."
        }

    # Mask tensor
    input_mask = tf.constant(input_mask_np, dtype=tf.bool)

    # Hitung skor
    intersection = tf.reduce_sum(tf.cast(tf.logical_and(recipe_matrix_binary, input_mask), tf.float32), axis=1)
    union = tf.reduce_sum(tf.cast(tf.logical_or(recipe_matrix_binary, input_mask), tf.float32), axis=1)
    final_scores = intersection / (union + 1e-6)

    # Cek perfect match
    perfect_match_indices = tf.where(final_scores >= 0.999).numpy().flatten()
    if len(perfect_match_indices) > 0:
        matched_titles = [recipe_titles[idx] for idx in perfect_match_indices]
        return {
            "recommendations": matched_titles,
            "message": "Resep relevan ditemukan!"
        }

    # Ambil Top-K jika tidak perfect match
    top_k_scores, top_k_indices = tf.nn.top_k(final_scores, k=num_recommendations)
    recommendations = [
        recipe_titles[top_k_indices[i].numpy()]
        for i in range(num_recommendations)
        if top_k_scores[i].numpy() >= min_score_threshold
    ]

    if recommendations:
        return {
            "recommendations": recommendations,
            "message": "Berikut rekomendasi resep yang mengandung bahan Anda."
        }
    else:
        return {
            "recommendations": [],
            "message": f"Tidak ada resep yang cocok (skor tertinggi < {min_score_threshold})."
        }

def save_model_assets(filepath: str, titles: list[str], ingredients: list[str], model: tf.keras.Model):
    model_assets = {
        "recipe_titles": titles,
        "ingredient_list": ingredients,
        "model_weights": model.get_weights()
    }
    with open(filepath, 'wb') as f:
        pickle.dump(model_assets, f)
    print(f"\n✅ Aset model disimpan ke: {filepath}")

def load_model_assets(filepath: str) -> tuple[tf.keras.Model, list[str], list[str]]:
    with open(filepath, 'rb') as f:
        assets = pickle.load(f)

    model = RecipeClassifier(len(assets["recipe_titles"]))
    _ = model(tf.zeros((1, len(assets["ingredient_list"]))))
    model.set_weights(assets["model_weights"])

    return model, assets["recipe_titles"], assets["ingredient_list"]