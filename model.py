from mistralai import Mistral
import os

model = "pixtral-12b-2409"

client = Mistral(api_key=os.getenv("MISTRAL_API_KEY"))


def get_model_response(command: str):
    return client.chat.complete(
        model=model,
        messages=[
            {
                "role": "user",
                "content": command,
            },
        ]
    ).choices[0].message.content
