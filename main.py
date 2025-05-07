import requests
import json
import time
import random
from bs4 import BeautifulSoup

with open('config.json') as config_file:
    config = json.load(config_file)

addresses = config.get('links', [])

for address in addresses:
    page = requests.get(address)
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
                ids = id_html.split('.')
                id = ids[0]
                #print(id)

                # finds extras, such as price, year, ect
                other_info = row.find_all('td', {'class': 'msga2-o pp6'})
                for info in other_info:
                    print(info.text)
    
    time.sleep(random.randint(1, 4)) # Waits a random time before the next request