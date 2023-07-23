from datetime import datetime
from bs4 import BeautifulSoup
import requests
import csv
from lxml import html
import numpy as np
import pandas as pd

fields=['url','substance']
tempDate=datetime.now().strftime("/%Y/%m/%d/")
url = 'https://www.rg.ru/news.html'
host ='https://rg.ru'
data=[]

response = requests.get(url)
bs = BeautifulSoup(response.text,"lxml")

def custom_selector(tag):
    return tag.name == "a" and tempDate in tag.get("href") and not tag.has_attr("class")

links=bs.find_all(custom_selector)

for link in links:
    substance=""
    url=host+link.get("href")

    response = requests.get(url)
    bs = BeautifulSoup(response.text,"lxml")

    title=bs.find("h1",class_={"PageArticleContent_title__RVnvC","PageArticleContent_title__JvolM"}).text
    content=bs.find("div",class_="PageContentCommonStyling_text__fCZrl")

    page_content = response.content
    tree = html.fromstring(page_content)
    paragraphs = tree.xpath("//p/text()")

    for paragraph in paragraphs:
        substance=substance+paragraph.replace("'", "").replace("[", "").replace("]", "").strip()

    substance=title+" "+substance

    data=[{"url":url,"substance":substance}]
    
    with open('data-rg.csv', 'a', newline='', encoding='utf-8-sig') as state_file:
        writer = csv.DictWriter(state_file, fields,delimiter=";")
        writer.writerows(data)
        state_file.close()

news = pd.read_csv('data-rg.csv',delimiter=";")

print(news)