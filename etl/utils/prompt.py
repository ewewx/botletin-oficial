import os
import time

import openai

from dotenv import load_dotenv
load_dotenv()

delimiter = "####"
MAX_TOKENS = 4096
openai.api_key  = os.getenv('OPENAI_API_KEY')


def get_completion(prompt, model="gpt-3.5-turbo"):
    messages = [{"role": "user", "content": prompt}]
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=0,
    )
    return response.choices[0].message["content"]

def summarize(content):
    prompt = f"""

        Generar un resumen del siguente texto utilizando \
        lenguaje sencillo siguiendo estas pautas pautas: \
        El texto generado no debe ser de mas de 350 caracteres. \
        El mensaje debe ser informativo, detallado, conciso y\
        orientado a un lector promedio sin conocimientos avanzados\
        en leyes, política o economía. \
        No debe incluirse la fecha de publicación. \
        No debe mencionarse su publición en el \
        Boletín Oficial bajo ningun concepto. \
        No debe incluir quienes son los que firman esta ley. \
        No debe incluir información de alguna sección o parrafo \
        que diga "publiquese" y "archivese". \


        Texto:{delimiter}{content}{delimiter}
    """

    response = get_completion(prompt)

    return response
