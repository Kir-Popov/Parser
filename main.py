from selenium import webdriver
from bs4 import BeautifulSoup
import requests
import json
import time


HOST = "https://play.google.com"


def get_html_selenium(url):
    driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver")  # Path of your Chrome webdriver
    driver.get(url)

    scroll_pause_time = 1
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_pause_time)  # Waiting downloading of scrolling page
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    main_page = driver.page_source
    driver.quit()
    return main_page


def brand_check(app_info, brand_name):
    brand_used = False
    for field in app_info:
        field = field.lower()
        if field.find(brand_name.lower()) != -1:
            brand_used = True
    return brand_used


def get_content(html, brand_name):
    start_time = time.time()
    soup = BeautifulSoup(html, 'html.parser')
    app_link_tag = soup.find_all('div', class_='b8cIId ReQCgd Q9MA7b')
    apps = []

    app_number = 0
    for link in app_link_tag:
        app_number += 1
        print("Working on app number", app_number)

        app_link = HOST + link.find('a').get('href')
        print(app_link)

        req = requests.get(app_link)
        if req.status_code == 200:
            app_page = requests.get(app_link).text
        else:
            continue

        #  parsing app page, all needed info in <main class = class_="LXrl4c">
        soup = BeautifulSoup(app_page, 'html.parser').find('main', class_="LXrl4c")

        try:
            name = link.find('div', class_="WsMG1c nnK0zc").text
        except AttributeError:
            name = "None"
            print("name None")

        try:
            author = soup.find('span', class_="T32cc UAO9ie").text
        except AttributeError:
            author = "None"
            print("author None")

        try:
            genre = soup.find('a', itemprop="genre").text
        except AttributeError:
            genre = "None"
            print("genre None")

        try:
            description = soup.find('div', jsname="sngebd").text
        except AttributeError:
            description = "None"
            print("description None")

        try:
            average_rating = soup.find('div', class_="BHMmbe").text
        except AttributeError:
            average_rating = "None"
            print("average_rating None")

        try:
            number_of_ratings = soup.find('span', class_="EymY4b").text
        except AttributeError:
            number_of_ratings = "None"
            print("number_of_ratings None")

        try:
            last_update = soup.find('span', class_="htlgb").text
        except AttributeError:
            last_update = "None"
            print("last_update None")

        print('\n')
        app_info = []
        app_info.extend([name, author, genre, description])  # app_info needed to check brand

        if brand_check(app_info, brand_name):
            apps.append(
                {
                    'Name': name,
                    'Link': app_link,
                    "Author": author,
                    "Category": genre,
                    "Description": description,
                    "Average rating": average_rating,
                    "Number of ratings": number_of_ratings,
                    "Last update": last_update
                }
            )

    print(app_number, 'apps was checked')
    print("--- %s seconds ---" % (time.time() - start_time), 'Work time')
    print("--- %s seconds ---" % ((time.time() - start_time) / app_number), 'Work time of checking one app')

    return apps


def to_json(apps):
    with open('apps.json', 'w') as f:
        json.dump(apps, f, sort_keys=False, indent=2, ensure_ascii=False)


def main():
    print("Enter brand name")
    brand_name = input()
    url = "https://play.google.com/store/search?q=" + brand_name + "&c=apps"
    html = get_html_selenium(url)
    apps = get_content(html, brand_name)
    to_json(apps)
    print('Check file apps.json')


if __name__ == '__main__':
    main()
