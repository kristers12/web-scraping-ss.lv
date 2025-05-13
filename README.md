# web scraping ss.lv
 
Projekta apraksts
-----------------

Darba galvenais uzdevums bija **apkopot filtrētus automašīnu sludinājumu datus no** [**ss.lv**](https://ss.lv) un tos apvienot vienā **Excel failā**, lai lietotājs varētu ātri pārlasīt tikai sev svarīgo informāciju.

Papildus uzdevums bija izveidot sistēmu, kas **paziņo lietotājam par jaunajiem sludinājumiem**, kas atbilst filtru kritērijiem.

Funkcionalitāte
---------------

*   Apkopot datus no ss.lv pēc lietotāja definētiem filtriem
    
*   Saglabāt rezultātus Excel failā
    
*   Sūtīt paziņojumus par jauniem atbilstošiem sludinājumiem uz Discord (ja funkcija ir ieslēgta)
    

Izmantotās bibliotēkas
----------------------

### Instalējamās:

*   requests – interneta lapaspušu nolasīšanai
    
*   bs4 (BeautifulSoup) – HTML koda apstrādei
    
*   pandas – Excel failu veidošanai un rediģēšanai
  
*   openpyxl - Excel failu lasīšanai, veidošanai un rediģēšanai
    
*   discord – Discord robota darbībai
    

### Standarta Python bibliotēkas:

*   threading – paralēlai darbībai starp programmu un Discord robotu
    
*   time – funkcionalitātei time.sleep()
    
*   random – nejaušu numuru ģenerēšanai priekš funkcijas time.sleep()
    
*   datetime – laika informācijas ierakstīšanai Excel failā
    

Konfigurācija
-------------

Pirms programmas palaišanas nepieciešams **rediģēt config.json failu**:

```json
{
    "links": [
        "https://www.ss.lv/lv/transport/cars/ford/",
        "https://www.ss.lv/lv/transport/cars/audi/",
        "https://www.ss.lv/lv/transport/cars/bmw/", 
        "https://www.ss.lv/lv/transport/cars/opel/",
        "https://www.ss.lv/lv/transport/cars/volvo/",
        "https://www.ss.lv/lv/transport/cars/volkswagen/",
        "https://www.ss.lv/lv/transport/cars/toyota/"

    ],
    "filters": {
        "pages_max": -1,
        "price_min": -1,
        "price_max": -1,
        "engine": "",
        "year": -1,
        "mileage_max": -1
    },
    "excel_file_name": "ss_autotest.xlsx",
    "scan_interval": 3600,
    "discord": {
        "enabled": true,
        "token": "YOUR_DISCORD_BOT_TOKEN",
        "channel_id": 1051528494586286154
    }
}
```

### Parametru skaidrojums

*   **links**: Masīvs ar ss.lv adresēm, kuras tiks skenētas
    
*   **filters**:
    
    *   price\_max: Maksimālā cena (piem., 10000)
        
    *   price\_min: Minimālā cena (piem., 2000)
        
    *   engine: Motora tips un tilpums (piem., "2.0D"). Ja neizmanto – ""
        
    *   year: Auto ražošanas gada minimums (piem., 2015)
        
    *   mileage\_max: Maksimālais nobraukums kilometros (piem., 200000)
        
    *   Ja kādu filtru nevēlas izmantot (izņemot engine), vērtība jābūt -1
        
*   **pages\_max**: Maksimālais pārlasāmo lapu skaits katrai adresei (max: 3)
    
*   **excel\_file\_name**: Saglabājamā Excel faila nosaukums
    
*   **scan\_interval**: Cik sekundes jāgaida starp datu atjauninājumiem (piem., 3600 – 1h)
    
*   **discord**:
    
    *   enabled: Vai paziņošanas funkcija ir ieslēgta (true / false)
        
    *   token: Discord bota token (jātur **privāti**!)
        
    *   channel\_id: Discord kanāla ID, kurā tiks sūtīti ziņojumi

Programma darbībā
-----------------
[![SS.lv Web Scraping Showcase](https://img.youtube.com/vi/0cD082Z4M0g/0.jpg)](https://www.youtube.com/watch?v=0cD082Z4M0g)
