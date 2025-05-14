import requests
import json
import time
import random
import threading
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime
from modules.car import Car, CarWebScraping


with open('config.json') as config_file:
    config = json.load(config_file)

# Get list of addresses and read filters for search
addresses = config.get('links', [])
filters = config.get('filters', {})
excel_file = config.get('excel_file_name', 'ss_auto.xlsx')
discord_enabled = config.get('discord', {}).get('enabled', False)


if discord_enabled:
    from modules.discord_bot import message_send, start_bot, client
    thread = threading.Thread(target=start_bot)
    thread.daemon = True
    thread.start()
    time.sleep(5)  # gaida kamer robots ir gatavs

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
engine_filter = filters.get('engine')
year_filter = filters.get('year')
mileage_filter = filters.get('mileage_max')
if mileage_filter == -1:
    mileage_filter = float('inf')
scan_interval = config.get('scan_interval', 3600)


#Programmas sākums
while True:
    data_now = {}
    data_updated = {}
    try:
        data_now = pd.read_excel(excel_file, sheet_name=None, engine='openpyxl')
    except Exception as e:
        print(f"Error loading data: {e}, file might not exist.") #Kļūda ja fails netiek atrasts
        
    ids = set()
    for address in addresses:
        subcategory = address.strip('/').split('/')[-1].capitalize()
        carWebScrape = CarWebScraping()
        

        for page_number in range (1, max_pages + 1):
            if page_number != 1:
                updated_address = address.rstrip('/') + f'/page{page_number}.html'
            else:
                updated_address = address

            print(f"Looking through: {updated_address}")
            
            page = requests.get(updated_address)
            if page.status_code == 200:
                page_content = BeautifulSoup(page.content, "html.parser")
                # atrod sludinājumu tabulu
                listing_table = page_content.find('table', {'align': 'center', 'cellpadding': '2', 'border': '0', 'width': '100%'})

                for row in listing_table.find_all('tr'):
                    #izfiltrē nevajadzīgās rindas
                    id = row.get('id')
                    split_id = id.split('_')
                    if split_id[0] == 'tr' and split_id[1].isdigit():
                        # atrod sludinājuma nosaukumu
                        title = row.find('td', {'class': 'msg2'}).find('a').get_text(strip=True)

                        # atrod linku uz sludinājumu
                        link_end = row.find('td', {'class': 'msg2'}).find('a').get('href')
                        link = "https://www.ss.com" + link_end

                        # atrod sludinajuma ID
                        link_parts = link.split('/')
                        id_html = link_parts[-1] # identifikators ar html
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
                        if len(engine_filter)>0:
                            if not engine_filter == engine:
                                continue
                        if not year_filter<=int(year):
                            continue
                        mileage = mileage.replace(" tūkst.", "")
                        if mileage.isdigit():
                            if int(mileage) >= mileage_filter:
                                continue

                        # atjaunot tipu Gada ievadei, jo panda nolasot pārveido par int skaitļus
                        year = str(year)

                        car = Car(id, title, link, model, year, engine, mileage, price, datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
                        carWebScrape.add(car)

            time.sleep(random.randint(1, 4)) # starp pieprasījumiem
        
        df_new = pd.DataFrame(carWebScrape.to_data())
        df_exist = data_now.get(subcategory, pd.DataFrame())

        #Check for data frames without a ID
        if df_new.empty or 'ID' not in df_new.columns:
                print(f"No 'ID' column found in {subcategory} data. Skipping.")
                continue

        # izmantojam, lai saglabātu visus datus, ja pat tie vairs nav pieejami mājaslapā, proti, veidojas kā datubāze
        if not df_exist.empty:
            ids_now = set(df_exist['ID'].astype(str))
            ids_new = set(df_new['ID'].astype(str))

            to_add = df_new[~df_new['ID'].astype(str).isin(ids_now)]
            if discord_enabled:
                if not to_add.empty:
                    client.loop.create_task(message_send(f"New cars found in {subcategory}: \n {to_add.to_string(index=False)}"))
            to_keep = df_exist[df_exist['ID'].astype(str).isin(ids_new)]

            df_final = pd.concat([to_keep, to_add], ignore_index=True)
        else:
            df_final = df_new

        data_updated[subcategory] = df_final

    # visu ierakstīt excel

    with pd.ExcelWriter(excel_file, engine='openpyxl', mode='w') as writer:
        for sheet, df in data_updated.items():
            df.to_excel(writer, sheet_name=sheet, index=False)
        print("Data saved to " + excel_file)
    print(f"Next scan in {scan_interval} secounds")
    time.sleep(scan_interval) #gaida nākamo pārskatīšanu