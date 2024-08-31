
import os
import time

from openai import OpenAI
import json

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

delimiter = "####"
MAX_TOKENS = 4096


def get_completion(prompt, model="gpt-4o-mini"):
    messages = [{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=model,
    messages=messages,
    temperature=0)
    return response.choices[0].message.content

def analyze(content):
    PROMPT = """Sos un periodista político en Argentina que sigue las renuncias y designaciones de los funcionarios del Gobierno de Argentina.  
        Necesito identificar en publicaciones del Boletín Oficial renuncias, designaciones y prórrogas. Tu trabajo es leer una publicación del boletín y encontrar y listar, en el caso de que haya, todas las renuncias, designaciones y prórrogas de cargos.
        Si para algun caso falta alguno de los campos obligatorios, no devuelvas esa designacion renuncia o prorroga. 
        Para cada renuncia y designación lista la siguiente información: 

        Cargo (cargo) - obligatorio
        Nombre (nombre) - obligatorio
        Documento Nacional de Identidad (dni) 
        Resolución (titulo de la resolución general)

        Devuelve el resultado en formato JSON, con tres listados: uno para designaciones, otro para renuncias y otro para prorrogas.
        Si no hay respuesta ni resolucion, devuelve un diccionario vacío. Siempre responde en formato JSON, sin usar el formating. "```json", directamente el codigo json plano.
        Resolución:
        """ + content

    response = get_completion(PROMPT)

    print(response)

    try:
        analysis_result = json.loads(response)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON from analyze function: {e}")
        print(f"Raw output from analyze function: {response}")
    
    return analysis_result
