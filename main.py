from fastapi import FastAPI

import model

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/model")
async def chat(command: str):
    try:
        print('command:', command)
        return model.get_model_response(command)
    except:
        raise Exception('Error in model response')