import requests
from lxml import html
from urllib.parse import urljoin
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time


def parse_product_page(url):
    response = requests.get(url)
    product_data = {}
    if response.status_code == 200:
        root = html.fromstring(response.content)
        product_name = root.xpath('//*[@id="container-20012ecdca"]/div/div[1]/div/div[1]/div/div[3]/div[1]/h1/span[2]/text()')
        if product_name:
            product_data['Название продукта'] = product_name[0].strip()
        product_description_elements = root.xpath('//div[@class="cmp-text"]')
        if product_description_elements:
            product_description = product_description_elements[0].text_content().strip()
            product_data['Описание продукта'] = product_description
        else:
            product_data['Описание продукта'] = "Не удалось найти информацию о продукте."
        product_data['Дополнительная информация'] = []
        service = webdriver.chrome.service.Service(r"C:\Users\vanag\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe")
        driver = webdriver.Chrome(service=service)
        try:
            driver.get(url)
            time.sleep(3)
            expand_button = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//*[@id="accordion-29309a7a60-item-9ea8a10642-button"]')))
            expand_button.click()
            nutrition_info = WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.XPATH, '//ul[@class="cmp-nutrition-summary__heading-primary"]')))
            for span in nutrition_info.find_elements(By.XPATH, './/span[@class="value"]'):
                value_text = span.text.strip()
                product_data['Дополнительная информация'].append(value_text)
        except TimeoutException:
            print("Превышено время ожидания элемента.")
        except Exception as e:
            print(f"Произошла ошибка: {str(e)}")
        finally:
            driver.quit()
    else:
        print("Ошибка при запросе страницы продукта.")
    return product_data


def parse_mcdonalds_menu(url):
    response = requests.get(url)
    menu_data = {}
    if response.status_code == 200:
        root = html.fromstring(response.content)
        xpath = '//*[@id="maincatcontent"]/div[4]/ul'
        menu_list = root.xpath(xpath)
        if menu_list:
            menu_items = menu_list[0].findall('.//li[@class="cmp-category__item"]')
            for item in menu_items:
                product_id = item.get('data-product-id')
                product_name = item.text.strip()
                product_url = item.find('a').get('href')
                product_url = urljoin(url, product_url)
                product_info = parse_product_page(product_url)
                menu_data[product_id] = product_info
                with open('mcdonalds_menu.json', 'w', encoding='utf-8') as f:
                    json.dump(menu_data, f, ensure_ascii=False, indent=4)
    else:
        print("Ошибка при запросе страницы.")


url = "https://www.mcdonalds.com/ua/uk-ua/eat/fullmenu.html"

parse_mcdonalds_menu(url)
