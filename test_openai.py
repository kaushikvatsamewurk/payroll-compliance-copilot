import os
from openai import OpenAI

print("KEY PREFIX:", os.environ.get("OPENAI_API_KEY")[:15])

client = OpenAI()

response = client.responses.create(
    model="gpt-4.1-mini",
    input="Say hello"
)

print("Response:", response.output_text)