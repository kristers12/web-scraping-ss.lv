import requests
import json
import time
import random
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# Datu struktūra priekš projekta
class Car:
    def __init__(self, id, description, url, model, year, engine, mileage, price, retrieved):
        self.id = id
        self.description = description
        self.url = url
        self.model = model
        self.year = year
        self.engine = engine
        self.mileage = mileage
        self.price = price
        self.retrieved = retrieved

    # pārveidot uz dictonary, lai vieglāk saglabāt excel fiel
    def to_dict(self):
        return {
            'ID': self.id,
            'Description': self.description,
            'URL': self.url,
            'Model': self.model,
            'Year': self.year,
            'Engine': self.engine,
            'Mileage': self.mileage,
            'Price': self.price,
            'Retrieved': self.retrieved
        }
        
class CarWebScraping:
    def __init__(self):
        self.cars = []

    def add(self, car):
        self.cars.append(car)
    
    def to_data(self):
        data = []
        for car in self.cars:
            car_dict = car.to_dict()
            data.append(car_dict)
        
        return data

with open('config.json') as config_file:
    config = json.load(config_file)

# Get list of addresses and read filters for search
addresses = config.get('links', [])
filters = config.get('filters', {})

# ierobežojumi priekš lapaspusem
max_pages = filters.get('pages_max')
if max_pages == -1:
    max_pages = 1
elif max_pages > 3:
    max_pages = 3

# ja config.json norādīts '-1', tad neievērot filtru
price_min = filters.get('price_min')
if price_min == -1:
    price_min = 0
price_max = filters.get('price_max')
if price_max == -1:
    price_max = float('inf')

data_now = {}
data_updated = {}

try:
    data_now = pd.read_excel("ss_auto.xlsx", sheetname=None, engine='openpyxl')
except:
    pass

for address in addresses:
    subcategory = address.strip('/').split('/')[-1].capitalize()
    carWebScrape = CarWebScraping()
    ids = set()

    for page_number in range (1, max_pages + 1):
        if page_number != 1:
            updated_address = address.rstrip('/') + f'/page{page_number}.html'
        else:
            updated_address = address

        print(f"Looking throguh: {updated_address}")
        
        page = requests.get(updated_address)
        if page.status_code == 200:
            page_content = BeautifulSoup(page.content, "html.parser")
            # Finds the table with the listings
            listing_table = page_content.find('table', {'align': 'center', 'cellpadding': '2', 'border': '0', 'width': '100%'})

            for row in listing_table.find_all('tr'):
                #Filters out the uneccesary rows
                id = row.get('id')
                split_id = id.split('_')
                if split_id[0] == 'tr' and split_id[1].isdigit():
                    # finds the title of the listing
                    title = row.find('td', {'class': 'msg2'}).find('a').get_text(strip=True)
                    #print(title)

                    # finds the link to the listing
                    link_end = row.find('td', {'class': 'msg2'}).find('a').get('href')
                    link = "https://www.ss.com" + link_end
                    #print(link)

                    # finds the unique id of the listing
                    link_parts = link.split('/')
                    id_html = link_parts[-1] # indentificator with the .html
                    id = id_html.split('.')[0]
                    ids.add(id)

                    # izgūst informāciju no klasēm 'msga2-o pp6' un 'msga2-r pp6'
                    info_o = []
                    info_values_o = row.find_all('td', {'class': 'msga2-o pp6'})
                    for value in info_values_o:
                        text = value.text.strip()
                        info_o.append(text)
                    info_r = []
                    info_values_r = row.find_all('td', {'class': 'msga2-r pp6'})
                    for value in info_values_r:
                        text = value.text.strip()
                        info_r.append(text)

                    if len(info_o) == 5:
                        model, year, engine, mileage, price = info_o
                    elif len(info_o) == 4 and len(info_r) == 1:
                        model, year, engine, price = info_o
                        mileage = info_r[0]
                    else:
                        continue
                    

                    # izlaiž sludinājumus, kur cilvēki grib pirkt mašīnas
                    if price == 'pērku':
                        continue

                    # Filtrs: izfiltrēt, skatoties pēc config.json uzstādītiem filtriem
                    price_digits = ''.join(filter(str.isdigit, price))
                    if price_digits:
                        price_value = int(price_digits) 
                    else: 
                        price_value = 0

                    if price_value < price_min or price_value > price_max:
                        continue

                    # atjaunot tipu Gada ievadei, jo panda nolasot pārveido par int skaitļus
                    year = str(year)

                    car = Car(id, title, link, model, year, engine, mileage, price, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                    carWebScrape.add(car)

        time.sleep(random.randint(1, 4)) # starp pieprasījumiem
    
    df_new = pd.DataFrame(carWebScrape.to_data())
    df_exist = data_now.get(subcategory, pd.DataFrame())

    # izmantojam, lai saglabātu visus datus, ja pat tie vairs nav pieejami mājaslapā, proti, veidajas kā datubāze
    if not df_exist.empty:
        ids_now = set(df_exist['ID'].astype(str))
        ids_new = set(df_new['ID'].astype(str))

        to_add = df_new[~df_new['ID'].astype(str).isin(ids_now)]
        to_keep = df_exist[df_exist['ID'].astype(str).isin(ids_new)]

        df_final = pd.concat([to_keep, to_add], ignore_index=True)
    else:
        df_final = df_new

    data_updated[subcategory] = df_final

# visu ierakstīt excel
with pd.ExcelWriter("ss_auto.xlsx", engine='openpyxl', mode='w') as writer:
    for sheet, df in data_updated.items():
        df.to_excel(writer, sheet_name=sheet, index=False)

print("Data saved to ss_auto.xlsx")
