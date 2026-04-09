===== FILE: min_requirements.txt =====
torch==1.10.0
===== END FILE =====

===== FILE: requirements.txt =====
beautifulsoup4==4.9.3
bs4==0.0.1
certifi==2021.5.30
charset-normalizer==2.0.4
idna==3.2
lxml==4.6.3
requests==2.26.0
soupsieve==2.2.1
urllib3==1.26.6

===== END FILE =====

===== FILE: Parsing/AvitoParser.py =====
import csv
import time
import json
import requests
import bs4

from Parsing.Page import Page


class AvitoParser:
    LOOP_DELAY = 5

    def __init__(self):
        self.url = None
        self.file_name = None
        self.params = None
        self.has_headers = False
        self.load_new_configs()

    def get_n_pages(self) -> int or None:
        """
        This function finds out number of pages for this theme.
        It returns None, if some error.
        :return: number of pages or None
        """
        try:
            request = requests.get(self.url)
            html = request.text
            soup = bs4.BeautifulSoup(html, "lxml")
            list_page_buttons = soup.select_one("div.pagination-root-Ntd_O").select('span')
            max_number_page = list_page_buttons[-2].text
            return int(max_number_page)
        except requests.exceptions.ConnectionError:
            print("Отсутствует соединение")
            return None

    def save_data(self, data: list) -> None:
        """
        This function saves data in a file named self.file_name
        """
        print("Сохранение")
        if not self.has_headers:
            headers = [key for key in self.params if self.params[key]]
            with open(self.file_name, 'w', newline='', encoding='utf-8') as csv_file:
                writer = csv.writer(csv_file, delimiter=';')
                writer.writerow(headers)
            self.has_headers = True

        with open(self.file_name, 'a', newline='', encoding='utf-8') as csv_file:
            writer = csv.writer(csv_file, delimiter=';')
            writer.writerows(data)

    def load_new_configs(self) -> None:
        """
        This function loads configs.json and fills properties
        If there is no configs.json, file will be created with default values
        """
        try:
            with open("Parsing/configs.json", 'r') as read_f:
                configs = json.load(read_f)
            self.url = configs['url']
            self.file_name = configs['file_name']
            self.params = configs['params']
        except FileNotFoundError:
            print("Отсутствует файл configs.json")

    def start(self) -> None:
        """
        This function is main loop for collecting and saving data
        """
        n_pages = range(self.get_n_pages())
        if not n_pages:
            return
        for number_page in n_pages:
            page = Page(self.url, number_page)
            data = page.get_data(self.params)
            if not data:
                return
            self.save_data(data)
            time.sleep(AvitoParser.LOOP_DELAY)

===== END FILE =====

===== FILE: Parsing/Handler.py =====
import bs4
import re
from abc import ABC, abstractmethod


class AbstractHandler(ABC):
    @abstractmethod
    def get_info(self, soup: bs4.BeautifulSoup) -> str or None:
        pass


class AboutApartmentBlockHandler(AbstractHandler):
    def __init__(self, key_word):
        self.key_word = key_word

    def get_info(self, soup: bs4.BeautifulSoup) -> str or None:
        text = soup.text
        if re.search(self.key_word, text) is None:
            return None
        else:
            index_end_of_string = re.search(self.key_word, text).span()[1]
            index_end_of_line = re.search("\n", text[index_end_of_string:]).span()[0] + index_end_of_string
            data = text[index_end_of_string: index_end_of_line]
            data = data.replace("\xa0", " ")
            return data.strip()


class AboutHouseBlockHandler(AbstractHandler):
    def __init__(self, key_word):
        self.key_word = key_word

    def get_info(self, soup: bs4.BeautifulSoup) -> str or None:
        text = soup.text
        if re.search(self.key_word, text) is None:
            return None
        else:
            index_end_of_string = re.search(self.key_word, text).span()[1]
            index_end_of_line = re.search("\n", text[index_end_of_string:]).span()[0] + index_end_of_string
            data = text[index_end_of_string: index_end_of_line]
            return data.strip()


class EmptyHandler(AbstractHandler):
    def get_info(self, soup: bs4.BeautifulSoup) -> str or None:
        return None


class PhysAddressHandler(AbstractHandler):
    def get_info(self, soup: bs4.BeautifulSoup) -> str or None:
        geo_block = soup.select_one("div.item-address")
        address = geo_block.text.strip().replace("\n", "|")
        return address


class NFloorsHandler(AbstractHandler):
    def get_info(self, soup: bs4.BeautifulSoup) -> str or None:
        text = soup.text
        index_begin_number = re.search("/", text).span()[1]
        index_end_number = re.search(" ", text[index_begin_number:]).span()[0] + index_begin_number
        return text[index_begin_number: index_end_number]


class ApartmentFloorHandler(AbstractHandler):
    def get_info(self, soup: bs4.BeautifulSoup) -> str or None:
        text = soup.text
        index_begin_number, index_end_number = re.search(r"[\d]+/", text).span()
        return text[index_begin_number: index_end_number-1]


class PriceHandler(AbstractHandler):
    def get_info(self, soup: bs4.BeautifulSoup) -> str or None:
        text = soup.text
        index_begin_price = re.search("Пожаловаться", text).span()[1]
        index_end_price = re.search("₽", text[index_begin_price:]).span()[0] + index_begin_price
        price = text[index_begin_price: index_end_price]
        return re.sub(r"\D", "", price)


class Distributor:
    def __init__(self, key: str):
        self.key = key

    def distribute(self) -> AbstractHandler:
        if self.key == "physical address":
            return PhysAddressHandler()
        elif self.key == "number of rooms":
            return AboutApartmentBlockHandler("Количество комнат:")
        elif self.key == "area of apartment":
            return AboutApartmentBlockHandler("Общая площадь:")
        elif self.key == "number of floors":
            return NFloorsHandler()
        elif self.key == "apartment floor":
            return ApartmentFloorHandler()
        elif self.key == "price":
            return PriceHandler()
        elif self.key == "repair":
            return AboutApartmentBlockHandler("Ремонт:")
        elif self.key == "bathroom":
            return AboutApartmentBlockHandler("Санузел:")
        elif self.key == "view from the windows":
            return AboutApartmentBlockHandler("Вид из окон:")
        elif self.key == "terrace":
            return AboutApartmentBlockHandler("Балкон или лоджия:")
        elif self.key == "year of construction":
            return AboutHouseBlockHandler("Год постройки:")
        elif self.key == "elevator":
            return AboutHouseBlockHandler("Пассажирский лифт:")
        elif self.key == "extra":
            return AboutHouseBlockHandler("В доме:")
        elif self.key == "type of house":
            return AboutApartmentBlockHandler("Тип дома:")
        elif self.key == "parking":
            return AboutApartmentBlockHandler("Парковка:")
        else:
            print("Встречен параметр, у которого отсутствует обработчик, параметр:", self.key)
            return EmptyHandler()

===== END FILE =====

===== FILE: Parsing/main.py =====
from AvitoParser import AvitoParser


if __name__ == "__main__":
    print("Начинается сбор квартир")
    parser = AvitoParser()
    parser.start()

===== END FILE =====

===== FILE: Parsing/Page.py =====
import time
import bs4
import requests

from Parsing.Post import Post


class Page:
    LOOP_DELAY = 7

    def __init__(self, url, page_number):
        self.url = url
        self.p_num = page_number

    def get_urls(self) -> list:
        """
        This function returns list of urls on apartments
        It uses self.url and self.p_num for creating request
        If there is connection error, it returns []
        """
        try:
            request = requests.get(self.url, params=dict(p=self.p_num))
            html = request.text
            soup = bs4.BeautifulSoup(html, "lxml")
            blocks = soup.select("div.iva-item-content-UnQQ4")
            urls = []
            for block in blocks:
                url = block.select_one('div.iva-item-titleStep-_CxvN').select_one('a').get('href')
                urls.append(url)
            return urls
        except requests.exceptions.ConnectionError:
            print("Отсутствует соединение")
            return []

    def get_data(self, params: dict) -> list:
        """
        This function returns list of data about apartments
        If there is connection error, it returns []
        If there is connection error after get_urls, it returns data
        """
        urls = self.get_urls()
        data = []
        for url in urls:
            try:
                post = Post(url)
                data.append(post.get_data(params))
                time.sleep(Page.LOOP_DELAY)
            except requests.exceptions.ConnectionError:
                return data
        return data

===== END FILE =====

===== FILE: Parsing/Post.py =====
from bs4 import BeautifulSoup
import requests

from Parsing.Handler import Distributor


class Post:
    domain = "https://www.avito.ru"

    def __init__(self, short_url):
        self.short_url = short_url

    def get_data(self, params: dict) -> list:
        """
        This function returns data of one apartments
        It uses parameters from params
        Connection error will be handle on class Page
        """
        full_url = Post.domain + self.short_url
        request = requests.get(full_url)
        print(full_url)
        if request.reason != 'OK':
            print("Возникла ошибка", request.reason)
        html = request.text
        soup = BeautifulSoup(html, "lxml")
        key_storage = dict()
        for key in [key for key in params if params[key]]:
            if key == "link":
                key_storage[key] = full_url
            else:
                handler = Distributor(key).distribute()
                try:
                    key_storage[key] = handler.get_info(soup)
                except AttributeError or TypeError:
                    key_storage[key] = None
        return list(key_storage.values())

===== END FILE =====

===== FILE: Parsing/parsing_tests/handlers_test.py =====
import unittest
import bs4
import json
from Parsing.Handler import *


def get_answers(key_word: str, right_answer: str, soup: bs4.BeautifulSoup):
    """
    This function returns values for assertEqual ('*' is required)
    It creates handler for key_word and get answer using soup
    """
    some_handle = Distributor(key_word).distribute()
    handle_answer = some_handle.get_info(soup)
    return right_answer, handle_answer


class TestHandler(unittest.TestCase):

    def test_get_right_answers_1(self):
        with open("parsing_test_1.html", 'r', encoding='utf-8') as f:
            html = f.read()
        soup = bs4.BeautifulSoup(html, "lxml")

        with open("right_answers_test_1.json", 'r', encoding='utf-8') as f:
            answers = json.load(f)

        for key in answers:
            self.assertEqual(*get_answers(key, answers[key], soup))

    def test_get_right_answers_2(self):
        with open("parsing_test_2.html", 'r', encoding='utf-8') as f:
            html = f.read()
        soup = bs4.BeautifulSoup(html, "lxml")

        with open("right_answers_test_2.json", 'r', encoding='utf-8') as f:
            answers = json.load(f)

        for key in answers:
            self.assertEqual(*get_answers(key, answers[key], soup))

    def test_get_right_answers_3(self):
        with open("parsing_test_3.html", 'r', encoding='utf-8') as f:
            html = f.read()
        soup = bs4.BeautifulSoup(html, "lxml")

        with open("right_answers_test_3.json", 'r', encoding='utf-8') as f:
            answers = json.load(f)

        for key in answers:
            self.assertEqual(*get_answers(key, answers[key], soup))

===== END FILE =====

===== FILE: Prediction/functions.py =====
import json
from math import sin, cos, asin, sqrt, pi
import torch
import torch.nn as nn


class BestModel(nn.Module):
    def __init__(self):
        super().__init__()
        self.seq = nn.Sequential(
            nn.BatchNorm1d(37),
            nn.Linear(37, 8),
            nn.ReLU(),
            nn.Linear(8, 1)
        )

    def forward(self, x):
        res = self.seq(x)
        return res


def get_dist(llong1, llat1, llong2, llat2):
    rad = 6372795
    lat1 = llat1 * pi / 180.
    lat2 = llat2 * pi / 180.
    long1 = llong1 * pi / 180.
    long2 = llong2 * pi / 180.
    delta_long = long2 - long1
    delta_lat = lat2 - lat1
    ad = 2 * asin(sqrt(sin(delta_lat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(delta_long / 2) ** 2))
    dist = ad * rad
    return dist


def get_amenities(lat, lon):
    with open("../amenities.json", 'r') as f:
        amenities = json.load(f)

    amenities_dict = dict()
    for cat_id, category in enumerate(amenities):
        amenities_dict[category] = 0
        for coordinates in amenities[category]:
            object_lat = coordinates[0]
            object_lon = coordinates[1]
            dist = get_dist(
                llong1=lon,
                llat1=lat,
                llong2=object_lon,
                llat2=object_lat
            )
            if dist < 5000:
                amenities_dict[category] += 1
    return amenities_dict


def get_price(data):
    perm_esplanade_lat = 58.010455
    perm_esplanade_lon = 56.229443

    lat = data[-2]
    lon = data[-1]
    amenities_dict = get_amenities(lat, lon)
    distance = get_dist(
        llong1=lon,
        llat1=lat,
        llong2=perm_esplanade_lon,
        llat2=perm_esplanade_lat
    )
    data.append(amenities_dict['edu'])
    data.append(amenities_dict['health'])
    data.append(amenities_dict['culture'])
    data.append(amenities_dict['eat'])
    data.append(distance)

    tensor = torch.tensor(data, dtype=torch.float32)
    model = BestModel()
    model.load_state_dict(torch.load('../best_model.pkl'))
    model.eval()
    predict = model(tensor.reshape(1, -1))
    return int(predict)

===== END FILE =====

===== FILE: Prediction/main.py =====
import tkinter as tk
from tkinter import ttk
from functions import get_price


def create_window():
    def calculate():
        try:
            data = [float(ent_n_rooms.get()), float(ent_area.get()), float(ent_n_floors.get()), float(ent_floor.get()),
                    float(ent_year.get()), float(ent_lift.get()), float(cmb_conc.current()), float(cmb_garbage.current())]
            repair_list = [0] * 4
            repair_list[cmb_repair.current()] = 1
            data += repair_list
            bath_list = [0] * 3
            bath_list[cmb_bath.current()] = 1
            data += bath_list
            terrace_list = [0] * 3
            terrace_list[cmb_terrace.current()] = 1
            data += terrace_list
            house_type_list = [0] * 5
            house_type_list[cmb_house_type.current()] = 1
            data += house_type_list
            district_list = [0] * 7
            district_list[cmb_district.current()] = 1
            data += district_list
            data.append(float(ent_lat.get()))
            data.append(float(ent_lon.get()))
            result = get_price(data)

            lbl_result['text'] = "Стоимость: " + str(round(result/1000_000, 3)) + " млн."
        except ValueError:
            pass

    root = tk.Tk()
    root.title("Предсказание стоимости квартиры")
    root.geometry("380x420")
    frame = tk.Frame(root)
    frame.pack()

    lbl_n_rooms = tk.Label(frame, text="Количество комнат")
    ent_n_rooms = tk.Entry(frame, width=20)
    lbl_n_rooms.grid(row=1, column=0)
    ent_n_rooms.grid(row=1, column=1, sticky="e")

    lbl_area = tk.Label(frame, text="Площадь")
    ent_area = tk.Entry(frame, width=20)
    lbl_area.grid(row=2, column=0)
    ent_area.grid(row=2, column=1, sticky="e")

    lbl_n_floors = tk.Label(frame, text="Количество этажей в доме")
    ent_n_floors = tk.Entry(frame, width=20)
    lbl_n_floors.grid(row=3, column=0)
    ent_n_floors.grid(row=3, column=1, sticky="e")

    lbl_floor = tk.Label(frame, text="Этаж квартиры")
    ent_floor = tk.Entry(frame, width=20)
    lbl_floor.grid(row=4, column=0)
    ent_floor.grid(row=4, column=1, sticky="e")

    lbl_year = tk.Label(frame, text="Год постройки")
    ent_year = tk.Entry(frame, width=20)
    lbl_year.grid(row=5, column=0)
    ent_year.grid(row=5, column=1, sticky="e")

    lbl_lift = tk.Label(frame, text="Количество лифтов")
    ent_lift = tk.Entry(frame, width=20)
    lbl_lift.grid(row=6, column=0)
    ent_lift.grid(row=6, column=1, sticky="e")

    lbl_conc = tk.Label(frame, text="Консьерж")
    cmb_conc = ttk.Combobox(frame, values=["Нет", "Есть"], width=16)
    cmb_conc.set("Выберите ответ")
    lbl_conc.grid(row=7, column=0)
    cmb_conc.grid(row=7, column=1, sticky="e", padx=5, pady=5)

    lbl_garbage = tk.Label(frame, text="Мусоропровод")
    cmb_garbage = ttk.Combobox(frame, values=["Нет", "Есть"], width=16)
    cmb_garbage.set("Выберите ответ")
    lbl_garbage.grid(row=8, column=0)
    cmb_garbage.grid(row=8, column=1, sticky="e", padx=5, pady=5)

    lbl_repair = tk.Label(frame, text="Ремонт")
    cmb_repair = ttk.Combobox(frame, values=["Дизайнерский", "Евро", "Косметический", "Требует ремонта"], width=16)
    cmb_repair.set("Выберите ответ")
    lbl_repair.grid(row=9, column=0)
    cmb_repair.grid(row=9, column=1, sticky="e", padx=5, pady=5)

    lbl_bath = tk.Label(frame, text="Санузел")
    cmb_bath = ttk.Combobox(frame, values=["Несколько", "Раздельный", "Совмещенный"], width=16)
    cmb_bath.set("Выберите ответ")
    lbl_bath.grid(row=10, column=0)
    cmb_bath.grid(row=10, column=1, sticky="e", padx=5, pady=5)

    lbl_terrace = tk.Label(frame, text="Балкон")
    cmb_terrace = ttk.Combobox(frame, values=["Балкон", "Лоджия", "Нет"], width=16)
    cmb_terrace.set("Выберите ответ")
    lbl_terrace.grid(row=11, column=0)
    cmb_terrace.grid(row=11, column=1, sticky="e", padx=5, pady=5)

    lbl_house_type = tk.Label(frame, text="Тип дома")
    cmb_house_type = ttk.Combobox(frame, values=["Блочный", "Деревянный", "Кирпичный", "Монолитный", "Панельный"],
                                  width=16)
    cmb_house_type.set("Выберите ответ")
    lbl_house_type.grid(row=12, column=0)
    cmb_house_type.grid(row=12, column=1, sticky="e", padx=5, pady=5)

    lbl_district = tk.Label(frame, text="Район")
    cmb_district = ttk.Combobox(frame, values=["Дзержинский", "Индустриальный", "Кировский", "Ленинский",
                                               "Мотовилихинский", "Орджоникидзевский", "Свердловский"],
                                width=16)
    cmb_district.set("Выберите ответ")
    lbl_district.grid(row=13, column=0)
    cmb_district.grid(row=13, column=1, sticky="e", padx=5, pady=5)

    lbl_lat = tk.Label(frame, text="Широта")
    ent_lat = tk.Entry(frame, width=20)
    lbl_lat.grid(row=14, column=0)
    ent_lat.grid(row=14, column=1, sticky="e")

    lbl_lon = tk.Label(frame, text="Долгота")
    ent_lon = tk.Entry(frame, width=20)
    lbl_lon.grid(row=15, column=0)
    ent_lon.grid(row=15, column=1, sticky="e")

    button = tk.Button(frame, text="Рассчитать стоимость", command=calculate)
    button.grid(row=16, column=0, padx=5, pady=5)
    lbl_result = tk.Label(frame, text="Стоимость: ")
    lbl_result.grid(row=16, column=1)

    root.mainloop()


if __name__ == "__main__":
    create_window()

===== END FILE =====