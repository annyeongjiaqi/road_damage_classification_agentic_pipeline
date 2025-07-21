import streamlit as st
from PIL import Image
from cnn_model import predict_damage
from get_geolocation import get_location
from llm_agent import generate_email
from mailer_agent import send_email

st.set_page_config(page_title="Road Damage Reporter")
st.title("Road Damage Detection and Reporting")

uploaded_file = st.file_uploader("Upload road image", type=["jpg", "png"])

if uploaded_file:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded Image", use_column_width=True)

    with st.spinner("Analyzing..."):
        result = predict_damage(image)
        st.write("Prediction:", result)

        if max(result.values()) > 0.8:
            damage_type = max(result, key=result.get)
            severity = result[damage_type]
            location = get_location()

            email_body = generate_email(damage_type, severity, location)
            send_email("authority@example.com", f"Road Damage Alert: {damage_type}", email_body)

            st.success("Report sent to authorities!")
        else:
            st.info("No significant damage detected.")
