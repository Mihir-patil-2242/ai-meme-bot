import os
import requests
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

# 🔐 Load API key from Streamlit secrets (not .env)
api_key = st.secrets["OPENROUTER_API_KEY"]

# 💬 Step 1: Generate Caption
def generate_caption(topic):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    body = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a meme expert. Generate short, funny captions. No explanations."},
            {"role": "user", "content": f"Generate a short, funny meme caption about: {topic}"}
        ]
    }

    try:
        response = requests.post(url, headers=headers, json=body)
        result = response.json()
        if "choices" in result:
            return result["choices"][0]["message"]["content"].strip()
        else:
            return "Oops! No caption generated."
    except Exception as e:
        return f"Error: {e}"

# 🖼️ Step 2: Add Caption to Image
def create_meme_image(caption, uploaded_img, font_path="impact.ttf", size=32):
    img = Image.open(uploaded_img)
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype(font_path, size)
    except:
        font = ImageFont.load_default()

    max_width = 40
    lines = []
    while len(caption) > max_width:
        space_index = caption.rfind(" ", 0, max_width)
        if space_index == -1:
            space_index = max_width
        lines.append(caption[:space_index])
        caption = caption[space_index:].strip()
    lines.append(caption)
    caption_text = "\n".join(lines)

    draw.text((10, 10), caption_text, font=font, fill="white")
    output_path = "web_meme.jpg"
    img.save(output_path)
    return output_path

# 🖥️ Step 3: Streamlit UI
st.set_page_config(page_title="AI Meme Generator", layout="centered")
st.title("🤖 AI Meme Generator")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "png"])
topic = st.text_input("Enter your meme topic")

if st.button("Generate Meme"):
    if not topic:
        st.warning("Please enter a meme topic.")
    elif not uploaded_file:
        st.warning("Please upload an image.")
    else:
        with st.spinner("Generating..."):
            caption = generate_caption(topic)
            meme_path = create_meme_image(caption, uploaded_file)

            # show image
            st.image(meme_path, caption=caption)

            # allow download
            with open(meme_path, "rb") as file:
                st.download_button(
                    label="📥 Download Meme",
                    data=file,
                    file_name="your_meme.jpg",
                    mime="image/jpeg"
                )

