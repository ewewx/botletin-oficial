import json
import time
import datetime

import openai

from utils import scraper, loader, prompt, preprocesser


def main():
    loader.new_json_today()
    urls, _ = scraper.today_urls()
    print(f"{len(urls)} Publications found.")
    print('***************')

    for i, url in enumerate(urls):
        print(f"Publication {i+1} of {len(urls)+1}")
        type, area, content, title, _ = scraper.scrape_article(url)
        print('Completed Scraping')


        resolution = preprocesser.resolute(content)
        date = datetime.date.today()
        print('Completed Preprocessing')

        try:
            summary = prompt.summarize(resolution)
        except (
            openai.error.APIConnectionError,
            openai.error.APIError,
            openai.error.ServiceUnavailableError,
            openai.error.Timeout,
        ) as error:
            print(error, "\n Retrying in 20s...")
            time.sleep(20)
            summary = prompt.summarize(resolution)

        print('Completed Extraction')

        publication = {
            'date': str(date),
            'area': area,
            'title': title, #Añadimos Title
            'url': url,
            'type': type,
            'summary': summary,
            'score': 0
        }

        print('Publication Created')

        loader.json_loader(publication)
        print("Loaded to json")
        print('***************')

if __name__ == "__main__":
    main()
