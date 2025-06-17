import os
import requests
from PIL import Image, ImageDraw, ImageFont
import streamlit as st

api_key = st.secrets["OPENROUTER_API_KEY"]

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
            {"role": "user", "content": f"Generate ONLY ONE short, funny meme caption about: {topic}. Do NOT return multiple lines, lists, examples, or explanations. Just return one sentence in plain text.No hashtags. No emojis. And funny."}


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

def create_meme_image(caption, uploaded_img, font_path="ComicNeue-Bold.ttf"):
    img = Image.open(uploaded_img)
    img_width = img.width
    size = 32

    try:
        font = ImageFont.truetype(font_path, size)
        print("✅ Custom font loaded")
    except Exception as e:
        print("❌ Font load failed:", e)
        font = ImageFont.load_default()

    import textwrap
    caption = caption.strip().replace('\n', ' ')
    wrapped = textwrap.fill(caption, width=30)

    draw = ImageDraw.Draw(img)

    # Adjust position (example: top center)
    bbox = draw.textbbox((0, 0), caption, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (img_width - text_width) // 2
    y = 30

    # Draw caption with stroke
    draw.text(
        (x, y),
        caption,
        font=font,
        fill="white",
        stroke_width=2,
        stroke_fill="black"
    )

    if img.mode != "RGB":
        img = img.convert("RGB")

    output_path = "web_meme.jpg"
    img.save(output_path, format="JPEG")
    return output_path




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

           
            st.image(meme_path, caption=caption)

           
            with open(meme_path, "rb") as file:
                st.download_button(
                    label="📥 Download Meme",
                    data=file,
                    file_name="your_meme.jpg",
                    mime="image/jpeg"
                )

