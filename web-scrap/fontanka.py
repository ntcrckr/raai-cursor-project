from datetime import datetime
from bs4 import BeautifulSoup
import requests
import csv
import numpy as np
import pandas as pd

fields=['url','substance']
tempDate=datetime.now().strftime("/%Y/%m/%d/")
url = 'https://www.fontanka.ru/24hours.html'
host='https://www.fontanka.ru'
data=[]

response = requests.get(url)
bs = BeautifulSoup(response.text,"lxml")

def custom_selector(tag):
    return tag.name == "a" and tag.has_attr("class") and "HTex" in tag.get("class") and tempDate in tag.get("href")

links=bs.find_all(custom_selector)

for link in links:
    substance=""
    url=host+link.get("href")

    response = requests.get(url)
    bs = BeautifulSoup(response.text,"lxml")

    title=bs.find("h1",class_="CHbj primaryH4HeadlineMobile primaryH2HeadlineTablet").text
    paragraphs=bs.find_all("div",class_="DRah JHa- JHah")
    
    for paragraph in paragraphs:
        substance=substance+paragraph.text

    substance=substance+" "+title
    
    data=[{"url":url,"substance":substance}]
    
    with open('data-fontanka.csv', 'a', newline='', encoding='utf-8-sig') as state_file:
        writer = csv.DictWriter(state_file, fields,delimiter=";")
        writer.writerows(data)
        state_file.close()

news = pd.read_csv('data-fontanka.csv',delimiter=";")

print(news)


