from datetime import datetime
from bs4 import BeautifulSoup
import requests
import csv
import numpy as np
import pandas as pd


def tv1():
    fields = ['url', 'substance']
    tempDate = datetime.now().strftime("/%Y-%m-%d/")
    url = 'https://www.1tv.ru/news'
    # _links = []
    data = []

    response = requests.get(url)
    bs = BeautifulSoup(response.text, "lxml")

    def custom_selector(tag):
        return tag.name == "a" and not tag.has_attr("class") and tempDate in tag.get("href") and not "vypusk_novostey" in tag.get("href")

    links = bs.find_all(custom_selector)

    for link in links[:10]:
        substance = ""
        url = link.get("href")
        # print(url)

        response = requests.get(url)
        bs = BeautifulSoup(response.text, "lxml")

        title = bs.find("h1", class_="title").text
        paragraphs = bs.find_all("div", class_="editor text-block active")

        for paragraph in paragraphs:
            substance = substance + paragraph.text

        substance = title + " " + substance
        # _links.append(url)
        data.append(f"{url}\n\n{substance}")
    #     data = [{"url": url, "substance": substance}]
    #
    #     with open('data-1tv.csv', 'a', newline='', encoding='utf-8-sig') as state_file:
    #         writer = csv.DictWriter(state_file, fields, delimiter=";")
    #         writer.writerows(data)
    #         state_file.close()
    #
    # news = pd.read_csv('data-1tv.csv', delimiter=";")
    #
    # return news
    return data


if __name__ == "__main__":
    print(tv1())
