import requests
from bs4 import BeautifulSoup
import json

url_base = "https://elcinema.com/tvguide/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
}

time_blocks = ["00:00", "06:00", "12:00", "18:00"]
channels_dict = {}

for t in time_blocks:
    try:
        response = requests.get(f"{url_base}?only_time={t}", headers=headers, timeout=20)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        tv_lines = soup.find_all('div', class_='tv-line')
        
        for line in tv_lines:
            channel_div = line.find('div', class_='channel')
            if not channel_div: continue
            
            img_tag = channel_div.find('img')
            name = ""
            for a in channel_div.find_all('a'):
                if a.get('title') and a.get('title') != "أضف إلى مفضلاتك":
                    name = a.get('title').strip()
                    break
            
            if not name: continue
            logo = img_tag.get('data-src') or img_tag.get('src', '') if img_tag else ""

            if name not in channels_dict:
                channels_dict[name] = {"channel_name": name, "channel_logo": logo, "programs": []}
            
            slots = line.find_all('div', class_='tv-slot')
            for slot in slots:
                lis = slot.find_all('li')
                if not lis: continue
                p_name = lis[0].text.strip()
                p_time = lis[-1].text.strip()
                p_type = " ".join(lis[1].text.split()) if len(lis) >= 3 else ""
                p_link = "https://elcinema.com" + lis[0].find('a')['href'] if lis[0].find('a') else ""

                entry = {"name": p_name, "time": p_time, "type": p_type, "link": p_link}
                if entry not in channels_dict[name]['programs']:
                    channels_dict[name]['programs'].append(entry)
    except:
        continue

final_list = list(channels_dict.values())
with open('chgede.json', 'w', encoding='utf-8') as f:
    json.dump(final_list, f, ensure_ascii=False, indent=4)