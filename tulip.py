#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().system('pip install selenium')
#get_ipython().system('apt update')
#get_ipython().system('pip install gspread oauth2client')
#get_ipython().system('pip install gspread_dataframe')
#get_ipython().system('pip install pyperclip')


# In[110]:


#SeleniumとBeautifulSoupのライブラリをインポート
import configparser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time
import datetime
import sys
import requests
from bs4 import BeautifulSoup
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from gspread_dataframe import set_with_dataframe

#configの読み込み
config_ini = configparser.ConfigParser()
config_ini.read('/Users/hitoshietoh/Documents/git/tulip/config.ini', encoding='utf-8')

Seed_key = config_ini['DEFAULT']['Seed_key']
Wallet_pass = config_ini['DEFAULT']['Wallet_pass']
Line_notify_token = config_ini['DEFAULT']['Line_notify_token']
Extension_path = config_ini['DEFAULT']['Extension_path']
Spreadsheet_key = config_ini['DEFAULT']['Spreadsheet_key']


# In[109]:


def send_line(notification_message):
    line_notify_token = Line_notify_token
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'{notification_message}'}
    requests.post(line_notify_api, headers = headers, data = data)


EXTENSION_PATH = Extension_path
options = Options()
options.add_extension(EXTENSION_PATH)
options.binary_location = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
driver_path = "/usr/local/bin/chromedriver"
drvr = webdriver.Chrome(options = options, executable_path = driver_path)

#solana tplチェック
drvr.switch_to.window(drvr.window_handles[0])
site_tpl = "https://solanabeach.io"
drvr.get(site_tpl)
time.sleep(5)
elem_solana_tpl = float(drvr.find_element(by=By.XPATH, value='//*[@id="app"]/div[3]/div/div/div/div[6]/div/div[1]/div/div[1]/div/div/p/span').text.replace(',',''))

#tplが2000以上だと実行
if elem_solana_tpl >= 2000:
    site ="https://tulip.garden/vaults"

    drvr.get(site)
    time.sleep(2)
    drvr.switch_to.window(drvr.window_handles[1])
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/div/div[2]/button[2]').click()
    time.sleep(1)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/div/div/div[2]/div/textarea').send_keys(Seed_key)
    time.sleep(5)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/button').click()
    time.sleep(5)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/button').click()
    time.sleep(4)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/div/div/div[2]/input').send_keys(Wallet_pass)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/div/div/div[2]/div/div/input').send_keys(Wallet_pass)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/div/div/div[3]/span/input').click()
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/button').click()
    time.sleep(3)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/button').click()
    time.sleep(3)
    #tulipのタブに切り替え
    drvr.switch_to.window(drvr.window_handles[0])
    time.sleep(3)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div[1]/div[1]/div[3]/div[1]').click()
    time.sleep(3)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div[1]/div[1]/div[3]/div[1]/div/button[1]').click()
    time.sleep(5)
    drvr.switch_to.window(drvr.window_handles[2])
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div/div[1]/div[2]/div/button[2]').click()
    time.sleep(3)
    drvr.switch_to.window(drvr.window_handles[0])
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div[1]/div[1]/div[1]/div[3]/div/button/span/span').click()
    time.sleep(1)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div[1]/div[1]/div[1]/div[3]/div/div/button[2]').click()
    time.sleep(2)
     #repairの判定
    time.sleep(1)
    if len(drvr.find_elements(by=By.CSS_SELECTOR, value='#root > div.app > div.app-body > div.infobar--error.infobar') )> 0 :
        send_line("REPAIR")
    else:
        #jsonファイルを使って認証情報を取得
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        c = ServiceAccountCredentials.from_json_keyfile_name('/Users/hitoshietoh//Documents/git/tulip/farming-345105-0f2eaff492a6.json', scope)

        #認証情報を使ってスプレッドシートの操作権を取得
        gs = gspread.authorize(c)

        SPREADSHEET_KEY = Spreadsheet_key
        worksheet = gs.open_by_key(SPREADSHEET_KEY).worksheet("2022-Mar")
        workbook = gs.open_by_key(SPREADSHEET_KEY)
        worksheet = workbook.worksheet('2022-Mar')

        #tulipのprofitをスプレッドシートに反映
        drvr.switch_to.window(drvr.window_handles[0])
        kills = []
        lps = []
        profits = []
        equities = []
        today = []
        item_lists = drvr.find_elements(by = By.CLASS_NAME, value='your-positions-table__row-item')
        for i in range(2,len(item_lists)+2):
            kill = drvr.find_element(by = By.XPATH, value=f'//*[@id="root"]/div[1]/div[2]/div/div[{i}]/div/div[5]').text.replace(' %','')
            kills.append(kill)
        for i in range(2,len(item_lists)+2):
            lp = drvr.find_element(by = By.XPATH, value=f'//*[@id="root"]/div[1]/div[2]/div/div[{i}]/div/div[1]/div/div[2]/div[1]').text
            lps.append(lp)
        for i in range(2,len(item_lists)+2):
            profit = drvr.find_element(by = By.XPATH, value=f'//*[@id="root"]/div[1]/div[2]/div/div[{i}]/div/div[4]/div[2]/div[1]/div[2]/span').text.replace('+$','')
            profits.append(profit)
        for i in range(2,len(item_lists)+2):
            equity = drvr.find_element(by = By.XPATH, value=f'//*[@id="root"]/div[1]/div[2]/div/div[{i}]/div/div[4]/div[1]').text.replace('$','').replace(',','')
            equities.append(equity)
        for i in range(2,len(item_lists)+2):
            date = str(datetime.datetime.now().year) + '年' + str(datetime.datetime.now().month) + '月' + str(datetime.datetime.now().day) + '日' + str(datetime.datetime.now().hour) + '時'
            today.append(date)
        df = pd.DataFrame()
        df['today'] = today
        df['lp'] = lps
        df['equities'] = equities
        df['profits'] = profits
        df['kills'] = kills
        sheetName = '2022-Mar'
        sh = gs.open_by_key('1msYrZ3Q3BbWygD0FXyQs4dili4aYeuiF5mnqFhf1K5g')
        sh.values_append(sheetName,
                         {'valueInputOption': 'USER_ENTERED'},
                         {'values': df.values.tolist()}
                         )
        drvr.switch_to.window(drvr.window_handles[0])
        #killer bufferを基準に必要あればアジャスト
        rows = 1
        for i in range(0,len(item_lists)):
            rows += 1
            elem_tulip_killer_buffer = float(kills[i])
            if elem_tulip_killer_buffer <= 17.33:
                drvr.find_element(by=By.XPATH, value=f'//*[@id="root"]/div[1]/div[2]/div/div[{i+2}]/div/div[7]/div[1]/button').click()
                #デポジット
                elem_tulip_input_usdc = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[2]/div[2]/div[2]/input').clear()
                time.sleep(0.5)
                elem_tulip_input_usdc = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[2]/div[2]/div[2]/input').send_keys(500)
                #borrow moreのチェック
                elem_tulip_borrowmore = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[3]').click()
                time.sleep(0.5)
                #借入比率をクリア
                elem_input_to_borrow = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[2]/div[2]/div[1]/div[3]/div/input').clear()
                #レバレッジ欄をクリア
                elem_tulip_3x = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[1]/div[2]/input').clear()
                time.sleep(0.5)
                #レバレッジを指定
                elem_tulip_3x = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[1]/div[2]/input').send_keys(3.0)
                #トークン価格を取得
                elem_tulip_token_price = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[2]/div[1]/div[3]')
                time.sleep(1)
                #借り入れた額を取得
                elem_tulip_borrow_amount = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[1]/div[1]').text
                #ポジション量を取得
                elem_tulip_ass_pos = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[7]/div[2]/div[2]').text.split(' ')
                elem_tulip_ass_borrow = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[7]/div[3]/div[2]').text.split(' ')
                #トークン価格を取得
                token_price = float(elem_tulip_token_price.text.split(' ')[3].replace('$',''))
                borrow_usdc = float(elem_tulip_borrow_amount.split(' ')[4].replace('$',''))
                #ポジション差を計算
                borrowed = borrow_usdc / token_price
                #必要
                need = float(elem_tulip_ass_pos[0].replace(',','')) - float(elem_tulip_ass_borrow[0].replace(',',''))
                #トークンとusdcの割合を計算
                r = (round((need / borrowed * 100),2))
                time.sleep(0.5)
                #rの値を入力
                time.sleep(0.5)
                elem_input_to_borrow = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[2]/div[2]/div[1]/div[3]/div/input').send_keys(r)
                print(elem_tulip_token_price)
                print(elem_tulip_ass_pos)
                print(elem_tulip_ass_borrow)
                elem_add_button = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[3]/button[2]').click()
                time.sleep(1)
                #注文確定
                drvr.switch_to.window(drvr.window_handles[2])
                elem_phantom_submit = drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div/div[1]/div/div[2]/div/button[2]').click()
            elif elem_tulip_killer_buffer >= 19.33:
                elem_tulip_coll = drvr.find_element(by=By.XPATH, value=f'//*[@id="root"]/div[1]/div[2]/div/div[{rows}]/div/div[7]/div[1]/button').click()
                #borrow moreのチェック
                elem_tulip_borrowmore = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[3]').click()
                #借入比率をクリア
                elem_input_to_borrow = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[2]/div[2]/div[1]/div[3]/div/input').clear()
                #レバレッジ欄をクリア
                elem_tulip_3x = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[1]/div[2]/input').clear()
                time.sleep(0.5)
                #レバレッジを指定
                elem_tulip_3x = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[1]/div[2]/input').send_keys(3.0)
                #トークン価格を取得
                elem_tulip_token_price = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[2]/div[1]/div[3]')
                time.sleep(1)
                #借り入れた額を取得
                elem_tulip_borrow_amount = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[1]/div[1]').text
                #ポジション量を取得
                elem_tulip_ass_pos = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[7]/div[2]/div[2]').text.split(' ')
                elem_tulip_ass_borrow = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[7]/div[3]/div[2]').text.split(' ')
                #トークン価格を取得
                token_price = float(elem_tulip_token_price.text.split(' ')[3].replace('$',''))
                borrow_usdc = float(elem_tulip_borrow_amount.split(' ')[4].replace('$',''))
                #ポジション差を計算
                borrowed = borrow_usdc / token_price
                #必要
                need = float(elem_tulip_ass_pos[0].replace(',','')) - float(elem_tulip_ass_borrow[0].replace(',',''))
                #トークンとusdcの割合を計算
                r = (round((need / borrowed * 100),2))
                time.sleep(0.5)
                #rの値を入力
                time.sleep(0.5)
                elem_input_to_borrow = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[2]/div[2]/div[1]/div[3]/div/input').send_keys(r)
                print(elem_tulip_token_price)
                print(elem_tulip_ass_pos)
                print(elem_tulip_ass_borrow)
                elem_add_button = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[3]/button[2]').click()
                time.sleep(1)
                #注文確定
                drvr.switch_to.window(drvr.window_handles[2])
                time.sleep(2)
                elem_phantom_submit = drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div/div[1]/div/div[2]/div/button[2]').click()
                drvr.switch_to.window(drvr.window_handles[0])
                time.sleep(180)
else:
    #TPLが2000以下だとLINE通知
    send_line('TPL IS LOW')
