from selenium import webdriver
from bs4 import BeautifulSoup
import json
import time
import asyncio
import aiohttp
import config


class GooglePlayParser:

    def __init__(self, brand_name):
        self._brand_name = brand_name
        self.driver = webdriver.Chrome(config.DRIVER_PATH)

    def _get_html_selenium(self, url):
        self.driver.get(url)

        scroll_pause_time = 1
        last_height = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)  # Waiting downloading of scrolling page
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        main_page = self.driver.page_source
        self.driver.quit()
        return main_page

    def _brand_check(self, app_info):  # Checking brand name in app info
        brand_used = False
        for field in app_info:
            field = field.lower()
            if field.find(self._brand_name.lower()) != -1:
                brand_used = True
        return brand_used

    async def _get_app_data(self, session, link):
        host = "https://play.google.com"
        app_link = host + link.find('a').get('href')
        try:
            async with session.get(app_link) as response:
                print(f"Working on {app_link}")
                html = await response.text()  # await

                #  parsing app page, all needed info in <main class = class_="LXrl4c">
                soup = BeautifulSoup(html, 'html.parser').find('main', class_="LXrl4c")

                try:
                    name = link.find('div', class_="WsMG1c nnK0zc").text
                except AttributeError:
                    name = "None"

                try:
                    author = soup.find('span', class_="T32cc UAO9ie").text
                except AttributeError:
                    author = "None"

                try:
                    genre = soup.find('a', itemprop="genre").text
                except AttributeError:
                    genre = "None"

                try:
                    description = soup.find('div', jsname="sngebd").text
                except AttributeError:
                    description = "None"

                try:
                    average_rating = soup.find('div', class_="BHMmbe").text
                except AttributeError:
                    average_rating = "None"

                try:
                    number_of_ratings = soup.find('span', class_="EymY4b").text
                except AttributeError:
                    number_of_ratings = "None"

                try:
                    last_update = soup.find('span', class_="htlgb").text
                except AttributeError:
                    last_update = "None"

                app_info = [name, author, genre, description]  # app_info needed to check brand

                if self._brand_check(app_info):
                    app = {
                        'Name': name,
                        'Link': app_link,
                        "Author": author,
                        "Category": genre,
                        "Description": description,
                        "Average rating": average_rating,
                        "Number of ratings": number_of_ratings,
                        "Last update": last_update
                    }
                    return app
        except Exception as e:
            print(e)
            return None

    async def _get_content(self, html):
        start_time = time.time()
        soup = BeautifulSoup(html, 'html.parser')
        apps_links_tag = soup.find_all('div', class_='b8cIId ReQCgd Q9MA7b')

        session_timeout = aiohttp.ClientTimeout(total=25)  # Timeout when request longer 25 seconds
        async with aiohttp.ClientSession(timeout=session_timeout) as session:
            apps = []
            for link in apps_links_tag:
                app = asyncio.ensure_future(self._get_app_data(session, link))
                apps.append(app)
            end_apps = await asyncio.gather(*apps)  # apps and None objects

        apps = []
        for app in end_apps:
            if app is not None:  # taking out None objects
                apps.append(app)
        print("--- %s seconds ---" % (time.time() - start_time), 'Work time')
        return apps

    def work(self):
        url = f"https://play.google.com/store/search?q={self._brand_name}&c=apps"
        html = self._get_html_selenium(url)
        apps = asyncio.run(self._get_content(html))
        return apps


def main():
    print('Enter brand name')
    brand_name = input()
    parser = GooglePlayParser(brand_name)
    apps = parser.work()

    with open('apps.json', 'w', encoding='utf-8') as f:
        json.dump(apps, f, sort_keys=False, indent=2, ensure_ascii=False)
    print('Check file apps.json')


if __name__ == '__main__':
    main()
