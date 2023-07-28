from datetime import datetime
from bs4 import BeautifulSoup
import requests
import csv
import numpy as np
import pandas as pd


def fontanka():
    fields = ['url', 'substance']
    tempDate = datetime.now().strftime("/%Y/%m/%d/")
    url = 'https://www.fontanka.ru/24hours.html'
    host = 'https://www.fontanka.ru'
    # _links = []
    data = []

    response = requests.get(url)
    bs = BeautifulSoup(response.text, "lxml")

    def custom_selector(tag):
        return tag.name == "a" and tag.has_attr("class") and "HTex" in tag.get("class") and tempDate in tag.get("href")

    links = bs.find_all(custom_selector)

    for link in links[:10]:
        try:
            substance = ""
            url = host + link.get("href")
            # print(url)

            response = requests.get(url)
            bs = BeautifulSoup(response.text, "lxml")

            title = bs.find("h1", class_="CLbh primaryH4HeadlineMobile primaryH2HeadlineTablet").text
            paragraphs = bs.find("div", class_="L3nx").children

            for paragraph in paragraphs:
                substance = substance+paragraph.text

            substance = title + " " + substance
            # _links.append(url)
            data.append(f"{url}\n\n{substance}")
        except Exception as e:
            # print(e)
            pass
    #     data = [{"url": url, "substance": substance}]
    #
    #     with open('data-fontanka.csv', 'a', newline='', encoding='utf-8-sig') as state_file:
    #         writer = csv.DictWriter(state_file, fields,delimiter=";")
    #         writer.writerows(data)
    #         state_file.close()
    #
    # news = pd.read_csv('data-fontanka.csv', delimiter=";")
    #
    # return news

    return data


if __name__ == "__main__":
    print(fontanka())
