import time
import random
import hashlib
import json
import requests
import datetime
import pandas as pd
from prj_clean_1 import clean_jsondata

url0 = 'http://cric-in.cricbigdata.com/'
getdataurl = 'SaleControl/ZZBInterface/GetData'
savecleandataurl = 'SaleControl/ZZBInterface/SaveCleanData'

appid = '1mvfQdq1DORaVHlwtnXxu8sgYnbcIz'
appSecret = '7lIKORuSqWdI8GKugtXBSvF'


def get_data_json(startnum):
    nonce = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba',8))
    timestamp = round(time.time()*1000)

    sign0 = f'appSecret={appSecret}&nonce={nonce}&timestamp={timestamp}'
    hsobj = hashlib.sha256(sign0.encode('utf-8'))

    sign = hsobj.hexdigest()


    url = f'{url0}{getdataurl}?{sign0}&appid={appid}&sign={sign}&iAutoID={startnum}'

    res = requests.get(url)
    return res



def upload_data(dataout):
    nonce = ''.join(random.sample('zyxwvutsrqponmlkjihgfedcba',8))
    timestamp = round(time.time()*1000)

    sign0 = f'appSecret={appSecret}&nonce={nonce}&timestamp={timestamp}'
    hsobj = hashlib.sha256(sign0.encode('utf-8'))

    sign = hsobj.hexdigest()

    posturl = f'{url0}{savecleandataurl}?appid={appid}&nonce={nonce}&timestamp={timestamp}&sign={sign}'

    postdata = dataout    

    res = requests.post(posturl,json=postdata)
    return res



def get_data_today(startnum0):
    dflist = []
    startnum = startnum0
    res = get_data_json(startnum)
    data = res.json()['data']
    lendata = len(data)
    while(lendata):
        dflist.append(pd.DataFrame(data))
        startnum += len(data)
        res = get_data_json(startnum)
        data = res.json()['data']
        lendata = len(data)    
    dfdata = pd.concat(dflist,ignore_index=True)
    return dfdata,startnum

def save_data_today(dfdata):
    today = datetime.date.today().strftime('%Y-%m-%d')
    filename = f'raw_data_{today}.xlsx'
    dfdata.to_excel(f'./data/{filename}',index=False)

def save_data_file(dfdata):
    filename = f'rawdata_{dfdata.iAutoID[0]}-{dfdata.iAutoID[df0.index[-1]]}.xlsx'
    dfdata.to_excel(f'./data/{filename}',index=False)

def main():

    with open('config.json','r') as f:
        xx = json.load(f)
        startnum = xx['startnum']

    dfdata,startnum = get_data_today(startnum)
    save_data_today(dfdata)


    dfout = clean_jsondata(dfdata)
    dataout = json.loads(dfout.to_json(orient='records'))

    res = upload_data(dataout)

    jsondata = {'startnum':startnum}
    with open('config.json','w') as f:
        f.write(json.dumps(jsondata,ensure_ascii=False))




def upload_clean_data(startnum,endnumx=99999999):
    dflist = []
    for i in range(5):
        dfdata,startnum = get_data_today(startnum)
        dflist.append(dfdata)
        if len(dfdata)< 1000:
            break
    df0 = pd.concat(dflist)