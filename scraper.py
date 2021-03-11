# scraper

import requests, re, datetime, time, sys, csv
import glob
import os
import itertools
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

from splinter import Browser
from random import seed, random

from settings import CHROMEDRIVER_DIR

def get_data(card):
    try:
        title = card.h2.text.strip()
        price = card.find('span', class_='a-offscreen').text
        # price = card.find('span', class_="a-price").find('span', class_='a-offscreen').text
        link = card.find('a', class_='a-link-normal a-text-normal').get('href')
        link = 'https://www.amazon.com' + link
        data = {"title": title, "price": price, "link": link}
        return data
    except:
        print("Error occurred with parsing data: ", sys.exc_info())
        return ''


def scraper(query):
    # define the location of the Chrome Driver - CHANGE THIS!!!!!
    executable_path = {'executable_path': CHROMEDRIVER_DIR}

    # Create a new instance of the browser, make sure we can see it (Headless = False)
    browser = Browser('chrome', **executable_path, headless=True)

    # define the components to build a URL
    method = 'GET'

    url = "https://www.amazon.com"
    # build the URL and store it in a new variable
    p = requests.Request(method, url).prepare()
    myurl = p.url

    # go to the URL
    browser.driver.set_window_size(1920, 1080)
    browser.visit(myurl)
    seed(1)
    time.sleep(random()+1)
    browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random()+1)
    browser.execute_script("window.scrollTo(document.body.scrollHeight, 0);")
    time.sleep(random()+1)
    query = query + "\n"
    
    try:
        browser.fill('field-keywords', query)
    except:
        print("Error occurred with searching: ", sys.exc_info())
        sys.exit()
    time.sleep(random()+1)

    # add a little randomness to using the page
    time.sleep(random()+random()*10+2)


    html = browser.html
    next_page_button = browser.find_by_css("li.a-last")
    time.sleep(random()+random()*10+2)
    next_page_button.click()
    time.sleep(random()+random()*10+2)
    
    # loop through all search results
    # limit to 10 pages for now
    x = 0
    while True:
        if x > 10:
            break
        try:
            # scroll to the bottom to trigger lazy loading
            browser.execute_script("var nextButton = document.querySelector('li.a-last'); nextButton.scrollIntoView({behavior: 'smooth', block: 'end', inline: 'nearest'});")
            time.sleep(random()+random()*10+2)
            # grab html
            html += browser.html
            time.sleep(random()+random()*10+2)
            # find next page button
            next_page_button = browser.find_by_css("li.a-last")
            # check to see if next button is disabled, which means it's time to end the loop and parse the data
            if next_page_button.has_class('a-disabled'):
                break
            print(next_page_button)
            next_page_button.click()
            time.sleep(random()+random()*10+2)
            x+=1
        except:
            print("Error handling pagination: ", sys.exc_info())
            break

    time.sleep(random()+random()*10+2)

    browser.quit()

    # create csv file with headers
    date = datetime.datetime.now()
    local_date = date.strftime("%x").replace("/", "_")
    local_time = date.strftime("%X").replace(":", "")
    query = query.replace(" ", "-").replace("\n", "")
    file_string = f"./results/{local_date}-{local_time}-{query}.csv"

    Path(file_string).touch()

    with open(file_string, 'w', newline="") as csvfile:
        fieldnames = ['Item Name', 'Price', 'Link']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
    csvfile.close()

    # parse data
    soup = BeautifulSoup(html, 'lxml')

    cards = soup.find_all('div', attrs={"data-asin": True, "data-component-type": "s-search-result"})

    info = [[],[],[]] # for storing all the info that's about to be parsed

    x=1
    for card in cards:
        data = get_data(card)
        print(data)
        if data:
            info[0].append(data["title"])
            info[1].append(data["price"])
            info[2].append(data["link"])
        x+=1

    # write scraped data to file
    df=pd.read_csv(file_string)

    # itertools is used here because sometimes there's asymmetry in the data
    for (a,b,c) in itertools.zip_longest(info[0], info[1], info[2]):
        row = [a,b,c]
        df.loc[len(df.index)] = row

    print("from scraper.py:")
    print(df.head())
    # print(df.dtypes)
    
    df.to_csv(path_or_buf=file_string)
    sys.exit()

scraper('air jordan')