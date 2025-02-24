import requests
from bs4 import BeautifulSoup
import sqlite3
import pandas as pd
import time

def parse_ads_for_urls(url_list, table_name):
    """
    Функция парсинга данных с сайта Kufar.
    :param url_list: список URL страниц для парсинга
    :param table_name: название таблицы в базе данных, в которую будут записываться данные
    """
    # Подключаемся к базе данных
    conn = sqlite3.connect("ads.db")
    cursor = conn.cursor()
    
    # Создаём таблицу, если её нет
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            price TEXT,
            district TEXT,
            url TEXT
        )
    ''')
    conn.commit()

    base_url = "https://www.kufar.by"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/90.0.4430.93 Safari/537.36'
    }
    
    for i, url in enumerate(url_list, start=1):
        print(f"Обрабатываем страницу: {i};") 
        
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            print(f"Ошибка запроса. Код: {response.status_code} для {url}")
            continue

        soup = BeautifulSoup(response.text, "html.parser")

        # Поиск блоков объявлений
        ad_blocks = soup.find_all("a", class_="styles_wrapper__5FoK7")
        if not ad_blocks:
            print("Объявления не найдены на странице:", url)
            continue

        data_list = []
        for ad_block in ad_blocks:
            # Название товара
            title_element = ad_block.find("h3", class_="styles_title__F3uIe")
            title = title_element.get_text(strip=True) if title_element else "Нет названия"

            # Цена
            price_element = ad_block.find("p", class_="styles_price__aVxZc")
            price = price_element.get_text(strip=True) if price_element else "Нет цены"

            # Район (district)
            district_element = ad_block.find("p", class_="styles_region__qCRbf")
            district = district_element.get_text(strip=True) if district_element else "Нет региона"

            # Ссылка на объявление
            ad_url = ad_block.get("href", "")
            if ad_url and not ad_url.startswith("http"):
                ad_url = base_url + ad_url

            data_list.append({
                "title": title,
                "price": price,
                "district": district,
                "url": ad_url
            })

        # Запись данных в БД
        if data_list:
            df = pd.DataFrame(data_list)
            df.to_sql(table_name, conn, if_exists="append", index=False)
            print(f"Сохранено {len(data_list)} объявлений с страницы: {i};\n")
        else:
            print("Нет данных для сохранения на странице:", url)
        
        time.sleep(1)  # Задержка между запросами

    conn.close()

# --- Вызов функции с примерами категорий ---
if __name__ == "__main__":
    guitars = [
         "https://www.kufar.by/l/r~minsk/gitary/hobbi-sport-i-turizm/bez-posrednikov?cnd=1&cursor=eyJ0IjoiYWJzIiwiZiI6dHJ1ZSwicCI6MywicGl0IjoiMjkwMDQwNjcifQ%3D%3D&mgsn=v.or%3A1&mgt=v.or%3A20&oph=1&sort=lst.d",
         "https://www.kufar.by/l/r~minsk/gitary/hobbi-sport-i-turizm/bez-posrednikov?cnd=1&cursor=eyJ0IjoiYWJzIiwiZiI6dHJ1ZSwicCI6MiwicGl0IjoiMjkwMDQwNjcifQ%3D%3D&mgsn=v.or%3A1&mgt=v.or%3A20&oph=1&sort=lst.d",
         "https://www.kufar.by/l/r~minsk/gitary/hobbi-sport-i-turizm/bez-posrednikov?cnd=1&cursor=eyJ0IjoiYWJzIiwiZiI6dHJ1ZSwicCI6MywicGl0IjoiMjkwMDQwOTMifQ%3D%3D&mgsn=v.or%3A1&mgt=v.or%3A20&oph=1&sort=lst.d"
    ]
    synthesizers = [
        "https://www.kufar.by/l/r~minsk/klavishnye/bez-posrednikov?mkb=v.or%3A1%2C25&mki=v.or%3A1%2C5&r_pageType=saved_search",
        "https://www.kufar.by/l/r~minsk/klavishnye/bez-posrednikov?cursor=eyJ0IjoiYWJzIiwiZiI6dHJ1ZSwicCI6MiwicGl0IjoiMjkwMDQzNDMifQ%3D%3D&mkb=v.or%3A1%2C25&mki=v.or%3A1%2C5&r_pageType=saved_search"
    ]
    parse_ads_for_urls(synthesizers, "synthesizers")
    parse_ads_for_urls(guitars, "guitars")
