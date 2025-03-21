import os
import numpy as np
import pandas as pd
import tensorflow as tf
from flask import Flask, request, render_template, redirect, url_for
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename
from tensorflow.keras.applications.resnet50 import preprocess_input

# Load trained model
model = tf.keras.models.load_model("model/food_classifier_resnet50.h5")
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

with open("model/class.txt", "r") as f:
    class_labels = [line.strip() for line in f.readlines() if line.strip()]
print(f"Class Labels: {class_labels}")
# Load recipe dataset
recipe_data = pd.read_csv("dataset/recipe_model.csv", encoding="ISO-8859-1")
recipe_data["Food_Item"] = recipe_data["Food_Item"].str.strip()

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = "static/uploads"

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(224, 224))
    img_array = image.img_to_array(img)
    img_array = preprocess_input(img_array)
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array

# Function to predict food item
def classify_food(img_path):
    img_array = preprocess_image(img_path)
    preds = model.predict(img_array)
    print(f"Prediction Raw Output: {preds}")
    class_index = np.argmax(preds)  # Get the highest confidence index
    print(f"Predicted Class Index: {class_index}")
    if class_index >= len(class_labels):
        return "Unknown Food"
    food_name = class_labels[class_index-1]  # Map to class labels from text file
    print(f"Predicted Food Name: {food_name}")
    return food_name

# Function to get recipe
def get_recipe(food_name):
    print(f"Looking for recipe of: {food_name}")
    match = recipe_data[recipe_data["Food_Item"].str.contains(food_name, case=False, na=False)]
    if not match.empty:
        print(f"Found Recipe: {match['Recipe'].values[0]}")
        return match["Recipe"].values[0]
    else:
        print("Recipe not found.")
        return "Recipe not found."

# Home route (Upload Form)
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        if "file" not in request.files:
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "" or not allowed_file(file.filename):
            return redirect(request.url)

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)

        # Predict food name
        food_name = classify_food(filepath)
        recipe = get_recipe(food_name)

        return render_template("index.html", food_name=food_name, recipe=recipe, image=filename)

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)
