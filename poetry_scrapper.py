import requests
import datetime
from bs4 import BeautifulSoup
import csv


BAD_THRESHHOLD = 1000


def load_bookmark():
    with open('bookmark.txt', 'r') as f:
        bookmark = f.read()
    bookmark_splited = bookmark.split('/')

    bookmark_year = int(bookmark_splited[-4])
    bookmark_month = int(bookmark_splited[-3])
    bookmark_day = int(bookmark_splited[-2])
    bookmark_poem_number = int(bookmark_splited[-1])

    page_dict = {
        'year': bookmark_year,
        'month': bookmark_month,
        'day': bookmark_day,
        'number': bookmark_poem_number,
    }
    return page_dict

def page_dict_to_url(page_dict):
    url = f"https://stihi.ru/{page_dict['year']}/{page_dict['month']}/{page_dict['day']}/{page_dict['number']}"
    return url

def flip_page(page_dict, count=1):
    if page_dict['number'] <= count:
        this_date = datetime.date(page_dict['year'], page_dict['month'], page_dict['day'])
        new_date = this_date - datetime.timedelta(1)
        
        page_dict['year'] = new_date.year
        page_dict['month'] = new_date.month
        page_dict['day'] = new_date.day
        page_dict['number'] = 5000
    
    else:
        page_dict['number'] -= count
    
    return page_dict

current_page = load_bookmark()

bad_status_in_a_row_count = 0
while bad_status_in_a_row_count < BAD_THRESHHOLD:

    url = page_dict_to_url(current_page)
    with open('bookmark.txt', 'w') as f:
        f.write(url)

    try:
        response = requests.get(url)
        status_code = response.status_code
    except:
        print('Connection error!')
        bad_status_in_a_row_count += 1
        status_code = 0

    if status_code != 200:
        print('Status code not 200. Initiating evasive maneuver')
        current_page = flip_page(current_page, count=1000)
    else:
        bad_status_in_a_row_count = 0
        
        soup = BeautifulSoup(response.text, 'html.parser')
        poem = soup.find('div', {'class': 'text'})
        if poem is None:
            current_page = flip_page(current_page)
            print('Skipping')
            continue
        poem = poem.text.strip()
        poem = poem.replace('\n', '|').replace('\xa0', '')

        with open('poems.csv', 'a', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([poem])

        current_page = flip_page(current_page)
        print(url)
        
else:
    print('Finished or stuck, go check something')
