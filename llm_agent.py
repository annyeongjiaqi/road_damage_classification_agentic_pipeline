from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()  # This loads your .env file into environment variables

email = os.getenv("EMAIL_USER")       
password = os.getenv("EMAIL_PASS")   
api_key = os.getenv("GEMINI_API_KEY")

llm = ChatOpenAI(temperature=0)

template = """
Write an email to the Land Transport Authority reporting road damage.
Include: damage type, severity (confidence score), time, date, and location (lat/lon).
Keep it professional and concise.

Damage type: {damage_type}
Severity score: {severity}
Location: {location}
Datetime: {timestamp}
"""

prompt = PromptTemplate.from_template(template)

def generate_email(damage_type, severity, location):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    chain = prompt | llm
    result = chain.invoke({
        "damage_type": damage_type,
        "severity": round(severity * 100, 2),
        "location": f"{location['lat']}, {location['lon']}",
        "timestamp": timestamp
    })
    return result.content
