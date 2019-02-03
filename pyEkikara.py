# -*- coding: utf-8 -*-0

import re
import json
import sys
from os import path
from urllib import request
from bs4 import BeautifulSoup
from urllib.parse import urljoin

detail_keys = { \
               '列車名': 'train_name', \
               '列車番号': 'train_id', \
               '列車予約コード': 'reservation_code', \
               '連結車両': 'cars', \
               '備考': 'remarks', \
               '運転日': 'dates', \
               }

def get_arr_dep_times(text):
    '''
    着発時刻を抽出する
    '''
    arr_suffix = '着'
    dep_suffix = '発'
    
    pattern = r'([0-9]{1,2}):([0-9]{1,2})(\S+)'
    matches = re.findall(pattern, text, \
                         flags = (re.MULTILINE | re.IGNORECASE))
    
    arrival_time = None
    departure_time = None
    
    for match in matches:
        if match[2] == arr_suffix:
            arrival_time = int(match[0] + match[1])
        
        if match[2] == dep_suffix:
            departure_time = int(match[0] + match[1])
    
    return arrival_time, departure_time
    
def get_train_details(detail_URL):
    '''
    各列車の詳細情報を取得する
    '''
    soup = BeautifulSoup(request.urlopen(detail_URL).read(), 'html.parser')
    tr_array = soup.findAll('tr')
    
    result = {}
    schedule = []
    
    for tr in tr_array:
        td_array = tr.findAll('td')
        
        if not 'class' in td_array[0].attrs.keys():
            continue
        
        if not 'lowBg06' in td_array[0].attrs['class']:
            continue
        
        key = td_array[0].text
        if key in detail_keys.keys():
            description = ''.join(td_array[1].text.split())
            result[detail_keys[key]] = description
        elif not td_array[0].find('a') is None:
            station = td_array[0].find('a').text
            arrival_time, departure_time = get_arr_dep_times(td_array[1].text)
            
            if (not arrival_time is None) and (not departure_time is None):
                schedule.append({'station': station, \
                                 'arrival_time': arrival_time, \
                                 'departure_time': departure_time, \
                                 })
    
    result['schedule'] = schedule

    return result

def extract_dict_from_script(script, pattern):
    '''
    Javascriptのコードから辞書型配列を抽出する
    '''
    matches = re.findall(pattern, script, \
                         flags = (re.MULTILINE | re.IGNORECASE)) 
    result = {}
    for match in matches:
        result[int(match[0])] = match[1]
    
    return result
        
def get_station_timetable(ekikara_URL, get_details = True, verbose = False):
    '''
    各駅の時刻表データを取得する
    '''
    # BeautifulSoupに取り込み
    html = request.urlopen(ekikara_URL).read()
    soup = BeautifulSoup(html, 'html.parser')
    
    # Javascriptのコードを抜き出す
    script_blocks = soup.findAll('script')
    script_code = ''
    for script in script_blocks:
        script_code = script_code + script.text
    
    # 種別・行先を抽出
    pattern_train = r'trainlegends\[([0-9]+?)\]\s*=\s*"([\s\S]+?)"'
    pattern_destination = r'destinationlegends\[([0-9]+?)\]\s*=\s*"([\s\S]+?)"'
    
    type_dict = extract_dict_from_script(script_code, pattern_train)
    dest_dict = extract_dict_from_script(script_code, pattern_destination)
    
    # 時刻表を抽出
    table = soup.find('td', {'class':'lowBg01'}).find('table').findAll('tr')
    
    # 時刻ごとに列車を抽出
    pattern_script = r'([0-9]+?)\s*,\s*([0-9]+?)'
    pattern_train_id = '([0-9]+[A-Z]*)'
    trains_array = []
    for tr in table:
        td_hour = tr.find('td', {'class':'lowBg06'})
        if (td_hour == None):
            continue
        
        # 時(hour)を取得
        hour = int(td_hour.text)
        if verbose:
            print('[%02d]' % hour)    
        
        # 列車を抽出
        inner_tr = tr.find('tbody').find('tr')
        td_train = inner_tr.findAll('td', {'id' : re.compile(r'[0-9]+?')})
        
        # 各列車に対する処理
        for td in td_train:
            # 分(minute)を取得
            minute = int(td.find('a').text)
            
            # 種別・行先を取得 (traintype, destination)
            openargs = re.findall(pattern_script, td['onmouseover'], \
                                  flags = (re.MULTILINE | re.IGNORECASE))
            traintype = type_dict[int(openargs[0][0])]
            destination = dest_dict[int(openargs[0][1])]
            
            if verbose:
                print('- %02d:%02d %s %s' % (hour, minute, traintype, destination))
            
            # 詳細情報を取得
            if get_details == True: 
                detail_URL = urljoin(ekikara_URL, td.find('a')['href'])
                details = get_train_details(detail_URL)
        
                train_id = re.findall(pattern_train_id, details['train_id'], 
                                      flags = (re.MULTILINE | re.IGNORECASE))
            else:
                details = {}
                train_id = ['']
            
            trains_array.append({ \
               'train_id':'-'.join(train_id), \
               'time':(hour*100+minute), \
               'type':traintype, \
               'dest':destination, \
               'details':details, \
               })
    
    return trains_array

if __name__ == '__main__':
    #URL = r'http://ekikara.jp/newdata/ekijikoku/1301131/up1_14205011.htm'
    
    if len(sys.argv) < 2:
        print('Usage: pyekikara ekikaraURL [--no-details] [--verbose]')
        sys.exit()

    URL = sys.argv[1]

    if '--no-details' in sys.argv:
        get_details = False
    else:
        get_details = True

    if '--verbose' in sys.argv:
        verbose = True
    else:
        verbose = False
    
    # 時刻表データを取得
    trains_array = get_station_timetable(URL, get_details, verbose)
    
    # CSVデータ生成
    if get_details == True:
        output_dat = 'time,type,dest,id,name,cars,remarks,dates\n'
    else:
        output_dat = 'time,type,dest\n'

    for train in trains_array:
        train_type = train['type']
        time = train['time']
        dest = train['dest']

        output_line = '%04d,%s,%s' % (time, train_type, dest)

        if get_details == True:
            for key in ['train_id', 'train_name', 'cars', 'remarks', 'dates']:
                output_line += (',"%s"' % train['details'][key])

        output_dat = output_dat + output_line + '\n'
        
    filenamebase, ext = path.splitext(path.basename(URL))
        
    #　抽出結果を保存（CSV）
    with open('%s.csv' % filenamebase, 'wt', encoding='shift-jis') as f:
        f.write(output_dat)
    
    # 抽出結果を保存（JSON）
    with open('%s.json' % filenamebase, 'wt', encoding='utf-8') as f:
        #json.dump(trains_array, f)
        f.write(json.dumps(trains_array))
