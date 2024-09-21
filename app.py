import streamlit as st
import bcrypt
from PIL import Image
import requests
from io import BytesIO
from keras.models import load_model
from firebase_setup import auth

def set_background(image_url):
    response = requests.get(image_url)
    img = Image.open(BytesIO(response.content))
    import base64
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_base64 = base64.b64encode(buffered.getvalue()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/jpeg;base64,{img_base64});
            background-size: cover;
            background-position: center;
            height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .login-container {{
            background-color: rgba(255, 255, 255, 0.8);
            padding: 2rem;
            border-radius: 8px;
            max-width: 50%;
            width: 50%;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
            text-align: left; 
        }}
        .login-container h2 {{
            margin-top: 0;
            font-size: 2rem;
            color: #333;
        }}
        .login-container input {{
            margin-top: 1rem;
            border-radius: 5px;
            border: 1px solid #ddd;
            width: calc(100% - 2rem);
            font-size: 0.875rem;
            padding: 0.5rem;
        }}
        .login-container .stButton {{
            margin-top: 1rem;
            background-color: #4CAF50;
            color: white;
            font-size: 0.875rem;
            padding: 0.5rem 1rem;
            border-radius: 5px;
        }}
        .login-container .stButton:hover {{
            background-color: #45a049;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

def signup():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2>Signup</h2>', unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Signup"):
        try:
            user = auth.create_user(email=email, password=password)
            st.success("Signup successful! Please login.")
            st.session_state["logged_in"] = False
        except Exception as e:
            st.error(f"Signup failed: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

def login():
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown('<h2>Login</h2>', unsafe_allow_html=True)
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        try:
            user = auth.get_user_by_email(email)
            if bcrypt.checkpw(password.encode(), user.password_hash.encode()):
                st.session_state["logged_in"] = True
                st.success("Login successful!")
                st.experimental_rerun()
            else:
                st.error("Invalid password")
        except Exception as e:
            st.error(f"Login failed: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

def disease_detection():
    set_background('dsa.jpg')
    st.markdown('<h1 style="color: black;">Disease Detection Model</h1>', unsafe_allow_html=True)
    disease = st.radio("Select Disease to Detect", ["Lung Cancer", "Alzheimer's Disease", "Pneumonia"])
    st.markdown('<h3 style="color: black;">Upload brain MRI image for Alzheimer, chest X ray of Pneumonia and Histopathological image for lung cancer</h3>', unsafe_allow_html=True)
    st.markdown('<h2 style="color: black;">Please upload the Medical image of the patient</h2>', unsafe_allow_html=True)
    file = st.file_uploader('', type=['jpeg', 'png', 'jpg'])

    if disease == "Alzheimer's Disease":
        model_path = 'keras_model1.h5'
        labels_path = 'labels1.txt'
    elif disease == "Lung Cancer":
        model_path = 'keras_model2.h5'
        labels_path = 'labels2.txt'
    elif disease == "Pneumonia":
        model_path = 'keras_model3.h5'
        labels_path = 'labels3.txt'

    model = load_model(model_path)

    with open(labels_path, 'r') as f:
        class_names = [a[:-1].split(' ')[1] for a in f.readlines()]
        f.close()
    print(class_names)

    if file is not None:
        image = Image.open(file).convert('RGB')
        resized_image = image.resize((224, 224))
        st.image(resized_image, use_column_width=True)
        class_name, conf_score = classify(resized_image, model, class_names, disease)
        st.markdown(f'<h3 style="color: #FF6347;">Class: {class_name}</h3>', unsafe_allow_html=True)
        st.markdown(f'<h4 style="color: #A0522D;">Confidence Score: {conf_score}</h4>', unsafe_allow_html=True)

def main():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False

    if st.session_state["logged_in"]:
        st.sidebar.success("Logged in")
        if st.sidebar.button("Logout"):
            st.session_state["logged_in"] = False
            st.experimental_rerun()
        disease_detection()
    else:
        option = st.sidebar.selectbox("Choose an option", ["Login", "Signup"])
        if option == "Login":
            login()
        elif option == "Signup":
            signup()

if __name__ == "__main__":
    main()
