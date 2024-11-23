from mistralai import Mistral

api_key = "XO5AGIwjxNz2zp7XXVvletaYqo7npFAS"
model = "pixtral-12b-2409"

client = Mistral(api_key=api_key)


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
