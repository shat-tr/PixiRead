import streamlit as st
import pytesseract
from PIL import Image
import os
from pathlib import Path
from dotenv import load_dotenv
from groq import Groq
#-----------
#UI
#------------
st.markdown("""
<style>
/* Main background */
html, body, [class*="css"]  {
    background: #eef6ff !important; 
    color: #0d1b2a !important;
}

/* Header container */
.pixi-header {
    background: linear-gradient(135deg, #1e3a8a, #3b82f6);
    padding: 28px;
    border-radius: 18px;
    text-align: center;
    color: white;
    box-shadow: 0 4px 18px rgba(0,0,0,0.12);
    margin-bottom: 30px;
}

/* Title text */
.pixi-title {
    font-size: 3rem;
    font-weight: 800;
    letter-spacing: 1px;
    color: #ffffff;
}

/* Subtitle */
.pixi-sub {
    font-size: 1.2rem;
    opacity: 0.95;
}

/* Mascot emoji size */
.pixi-mascot {
    font-size: 3.2rem;
    margin-right: 10px;
}

/* Cute Loader */
.pixi-loader {
    text-align: center;
    margin-top: 15px;
}

.pixi-loader span {
    display: inline-block;
    width: 12px;
    height: 12px;
    margin: 4px;
    background: #3b82f6;
    border-radius: 50%;
    animation: pixi-bounce 0.6s infinite alternate;
}

.pixi-loader span:nth-child(2) { animation-delay: .15s }
.pixi-loader span:nth-child(3) { animation-delay: .3s }

@keyframes pixi-bounce {
    to { transform: translateY(-6px); opacity: .5; }
}

</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="pixi-header">
    <span class="pixi-mascot">🧚‍♀️</span>
    <span class="pixi-title">PixiRead</span>
    <div class="pixi-sub">Scan • Understand • Translate ✨</div>
</div>
""", unsafe_allow_html=True)

# ------------------------------
# Load API Key from .env
# ------------------------------
env_path = Path(__file__).parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ GROQ_API_KEY missing. Add it to your .env file.")
    st.stop()

client = Groq(api_key=api_key)

# ------------------------------
# Helper Functions
# ------------------------------

def extract_text_from_image(image):
    """Extract text using Pytesseract"""
    try:
        return pytesseract.image_to_string(image)
    except Exception as e:
        return f"Error extracting text: {e}"


def ask_question_from_text(text, question):
    """Ask a question about extracted text"""
    try:
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You answer questions based ONLY on the provided text."},
                {"role": "user", "content": f"Text: {text}\n\nQuestion: {question}"}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ API Error: {e}"


def translate_text(text, language):
    """Translate text to selected language"""
    if language == "None":
        return None

    try:
        prompt = f"Translate the following text into {language}:\n\n{text}"

        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a translation assistant."},
                {"role": "user", "content": prompt}
            ]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"❌ Translation Error: {e}"


# ------------------------------
# UI Starts
# ------------------------------

st.set_page_config(page_title="PixiRead App", layout="wide")

# ----- IMAGE UPLOAD -----
uploaded_file = st.file_uploader("Upload an image", type=["png", "jpg", "jpeg"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    extracted_text = extract_text_from_image(image)

    st.subheader("📌 Extracted Text:")
    st.info(extracted_text)

    # ----- Translation Section -----
    st.subheader("🌐 Select Translation Language:")
    language = st.selectbox(
        "Choose a language:",
        ["None", "Hindi", "Marathi", "Gujarati", "Tamil", "Telugu", "Kannada", "French", "Spanish", "German"],
        index=0
    )

    if language != "None":
        translation = translate_text(extracted_text, language)
        if translation:
            st.subheader(f"🌍 Translation in {language}:")
            st.success(translation)

    # ----- Q&A Section -----
    st.subheader("❓ Ask a question about the extracted text")
    user_question = st.text_input("Enter your question:")

    if st.button("Get Answer"):
        if user_question.strip() == "":
            st.warning("Please enter a question.")
        else:
            answer = ask_question_from_text(extracted_text, user_question)
            st.subheader("🤖 AI Answer:")
            st.info(answer)
