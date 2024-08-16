import json
import os
from datetime import datetime


# Get today's date
today = datetime.today()
# Format the date as YYYY MM DD
formatted_date = today.strftime("%Y-%m-%d")


FILE = 'data_'+formatted_date+'.json'

def json_loader(
        entry: dict,
        file: str = FILE,
) -> None:
    with open(file, "r+") as file:
        data = json.load(file)
        data.append(entry)
        file.seek(0)
        json.dump(data, file)

def new_json_today():
    with open(FILE, "w") as today_file:
        today_file.write("[]")
