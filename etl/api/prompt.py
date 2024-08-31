
import os
import time

import openai

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

def analyze(content):
    PROMPT = """Sos un periodista político en Argentina que sigue las renuncias y designaciones de los funcionarios del Gobierno de Argentina.  
        Necesito identificar en publicaciones del Boletín Oficial renuncias, designaciones y prórrogas. Tu trabajo es leer una publicación del boletín y encontrar y listar, en el caso de que haya, todas las renuncias, designaciones y prórrogas de cargos.
        Si no se encuentra la fecha efectiva en el documento llenar el campo con “null”
        Para cada renuncia y designación lista la siguiente información: 

        Cargo (cargo)
        Nombre (nombre)
        Documento Nacional de Identidad (dni) 
        Resolución (titulo de la resolución general)

        Devuelve el resultado en formato JSON, con tres listados: uno para designaciones, otro para renuncias y otro para prórrogas.
        
        Resolución:
        """ + content


    response = get_completion(PROMPT)

    return response
