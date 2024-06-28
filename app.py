import streamlit as st
import tensorflow as tf
import numpy as np
from utils import load_and_prep_image, plot_top_10_probs, load_image_from_url, load_image_from_base64
from config import MODEL_PATH
import os
import re

# Load the trained model
model = tf.keras.models.load_model(MODEL_PATH)

class_names = ['apple_pie', 'baby_back_ribs', 'baklava', 'beef_carpaccio', 'beef_tartare', 'beet_salad', 'beignets', 'bibimbap',
                'bread_pudding', 'breakfast_burrito', 'bruschetta', 'caesar_salad', 'cannoli', 'caprese_salad', 'carrot_cake', 
                'ceviche', 'cheesecake', 'cheese_plate', 'chicken_curry', 'chicken_quesadilla', 'chicken_wings', 'chocolate_cake',
                'chocolate_mousse', 'churros', 'clam_chowder', 'club_sandwich', 'crab_cakes', 'creme_brulee', 'croque_madame',
                'cup_cakes', 'deviled_eggs', 'donuts', 'dumplings', 'edamame', 'eggs_benedict', 'escargots', 'falafel', 'filet_mignon',
                'fish_and_chips', 'foie_gras', 'french_fries', 'french_onion_soup', 'french_toast', 'fried_calamari', 'fried_rice',
                'frozen_yogurt', 'garlic_bread', 'gnocchi', 'greek_salad', 'grilled_cheese_sandwich', 'grilled_salmon', 'guacamole',
                'gyoza', 'hamburger', 'hot_and_sour_soup', 'hot_dog', 'huevos_rancheros', 'hummus', 'ice_cream', 'lasagna',
                'lobster_bisque', 'lobster_roll_sandwich', 'macaroni_and_cheese', 'macarons', 'miso_soup', 'mussels', 'nachos',
                'omelette', 'onion_rings', 'oysters', 'pad_thai', 'paella', 'pancakes', 'panna_cotta', 'peking_duck', 'pho',
                'pizza', 'pork_chop', 'poutine', 'prime_rib', 'pulled_pork_sandwich', 'ramen', 'ravioli', 'red_velvet_cake',
                'risotto', 'samosa', 'sashimi', 'scallops', 'seaweed_salad', 'shrimp_and_grits', 'spaghetti_bolognese',
                'spaghetti_carbonara', 'spring_rolls', 'steak', 'strawberry_shortcake', 'sushi', 'tacos', 'takoyaki',
                'tiramisu', 'tuna_tartare', 'waffles']

def preprocess_and_predict(img):
    img = tf.image.resize(img, [224, 224])
    img = tf.expand_dims(img / 255.0, axis=0)
    
    pred_prob = model.predict(img)[0]
    pred_class = class_names[np.argmax(pred_prob)]

    st.write(f"Predicted class: {pred_class}")
    fig = plot_top_10_probs(pred_prob, class_names)
    st.plotly_chart(fig)

st.title("Food Image Classification")
st.write("Upload an image of food, and the model will predict its category.")

# Create a two-column layout
# Create a two-column layout
cols = st.columns([1, 2])

# Left column for upload and URL input
with cols[0]:
    st.markdown("""
        <div style="border: 1px solid #ddd; padding: 10px; border-radius: 5px; text-align: center;">
            <p style="margin: 0;">Drag and Drop your file here</p>
            <p style="margin: 0;">or</p>
            <div style="margin-bottom: 10px;">
                <input type="file" accept=".jpg, .jpeg" onchange="window.streamlitSendData({files: this.files})">
            </div>
            <p>enter your url/base64</p>
        </div>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader(" ", type=["jpg", "jpeg"], accept_multiple_files=False)
    st.text_input("", key="image_url", placeholder="Or enter an image URL or base64 data...")


# Right column for displaying the loaded image
with cols[1]:
    if uploaded_file is not None:
        temp_file_path = os.path.join("temp", uploaded_file.name)
        with open(temp_file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.image(temp_file_path, caption='Processing...', use_column_width=True)
        img = load_and_prep_image(temp_file_path)
        os.remove(temp_file_path)
    elif st.session_state.image_url:
        image_url = st.session_state.image_url
        if re.match(r'^data:image\/[a-zA-Z]+;base64,', image_url):
            img = load_image_from_base64(image_url)
        else:
            img = load_image_from_url(image_url)
        st.image(img.numpy(), caption='Processing...', use_column_width=True)

# Display the plot in a full-width row below
if uploaded_file is not None or st.session_state.image_url:
    st.markdown("---")
    if uploaded_file is not None:
        preprocess_and_predict(img)
    elif st.session_state.image_url:
        preprocess_and_predict(img)
