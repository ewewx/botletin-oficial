import datetime

from jinja2 import Environment, FileSystemLoader

from utils.reader import reader
from utils.preprocesser import sort_by
from utils.ranker import ranker
from utils.mailing import send_mail
import json

today = str(datetime.datetime.today().strftime('%Y-%m-%d'))
FILEPATH = 'data_'+today+'.json'

def main():
    #Levanta la info del JSON
    data = reader(FILEPATH)
    #Por cada publicacion las ordena por su valor de Score
    data = ranker(data, threshold=0)
    data = sort_by(data)


    """ #¿Es el set() creado un Diccionario de Types, o es el Type de cada entrada?
    #Hemos cambiado todos los "data" por "data_string" dado que queremos trabajar con el objeto.
    for type in set([x['type'] for x in data_string]):
        mail_content += "<h2>"+type+"</h2><br/><br>"
        for result in data_string:
            if result["type"] == type:
                mail_content += "<h5>"+result["area"]+"</h5><br>"
                mail_content += "<p>"+result["summary"]+"</p><br>"
                mail_content += '<a href="' + result["url"] + '">Ver publicación</a>' """



    env = Environment(loader=FileSystemLoader('templates'))
    template = env.get_template('README.md.j2')
    rendered_readme = template.render(results=data, today=today, types=set([x['type'] for x in data]))


    with open("README.md", "w+") as f:
        f.write(rendered_readme)

    send_mail(rendered_readme, "Prueba de Scrapeo y envio por mail", ["carlohigue@gmail.com", ""])

if __name__ == "__main__":
    main()
