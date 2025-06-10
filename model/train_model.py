from model import RecipeClassifier, save_model_assets
import pandas as pd
import tensorflow as tf
import numpy as np

df = pd.read_csv('./data/resep_tfidf_features.csv')
recipe_titles = df.iloc[:, 0].tolist()
X_features_df = df.iloc[:, 1:]
ingredient_list = X_features_df.columns.tolist()

recipe_matrix_binary = tf.constant(X_features_df.values > 0, dtype=tf.bool)
X_train = recipe_matrix_binary.numpy().astype(np.float32)
y_train = np.arange(len(recipe_titles))

model = RecipeClassifier(len(recipe_titles))
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=50, batch_size=32)

save_model_assets("model/recipe_model.pkl", recipe_titles, ingredient_list, model)
