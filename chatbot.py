from dotenv import load_dotenv
load_dotenv() 

import os
import streamlit as st
from datetime import datetime
from get_geolocation import GeoLocationTool
from llm_agent import EmailTool
from mailer_agent import MailerTool
from cnn_model import predict_damage

st.set_page_config(
    page_title="Road Damage Detection (Agentic)",
    page_icon="🛣️",
)

st.title("Road Damage Detection (Agentic)")

# 1. Upload an image
uploaded_image = st.file_uploader("Upload road image", type=["jpg","jpeg","png"])

# 2. Process on button click
if uploaded_image and st.button("Report Damage"):
    with st.spinner("Processing..."):
        # Read bytes
        image_bytes = uploaded_image.getvalue()
        
        # a) Classify damage via CNN
        damage_type = predict_damage(image_bytes)
        st.write(f"Detected damage: {damage_type}")

        # b) If damage, get location and notify
        if damage_type.lower() != "no damage":
            # Geolocation
            location = GeoLocationTool().run(image_bytes)

            # Compose report
            damage_info = (
                f"Type: {damage_type}; "
                f"Location: {location}; "
                f"Time: {datetime.now():%Y-%m-%d %H:%M:%S}"
            )

            # Generate and send email
            email_body = EmailTool().run(damage_info)
            MailerTool().run(email_body)

            st.success("Damage report sent to authorities.")
        else:
            st.info("No road damage detected.")