#!/usr/bin/env python
# coding: utf-8

# In[1]:


#get_ipython().system('pip install selenium')
#get_ipython().system('apt update')
#get_ipython().system('pip install gspread oauth2client')
#get_ipython().system('pip install gspread_dataframe')
#get_ipython().system('pip install pyperclip')


# In[39]:


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
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
#configの読み込み
config_ini = configparser.ConfigParser()
config_ini.read('/Users/hitoshietoh/Documents/git/tulip/config.ini', encoding='utf-8')

Seed_key = config_ini['DEFAULT']['Seed_key']
Wallet_pass = config_ini['DEFAULT']['Wallet_pass']
Line_notify_token = config_ini['DEFAULT']['Line_notify_token']
Extension_path = config_ini['DEFAULT']['Extension_path']
Spreadsheet_key = config_ini['DEFAULT']['Spreadsheet_key']
deposit_amount = config_ini['DEFAULT']['deposit_amount']
sheet_name = config_ini['DEFAULT']['sheet_name']
json_key = config_ini['DEFAULT']['json_key']
binary_location = config_ini['DEFAULT']['binary_location']
driver_path = config_ini['DEFAULT']['driver_path']


def send_line(notification_message):
    line_notify_token = Line_notify_token
    line_notify_api = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {line_notify_token}'}
    data = {'message': f'{notification_message}'}
    requests.post(line_notify_api, headers = headers, data = data)
    
def wait_visible(xpath):
    WebDriverWait(drvr, 30).until(
        EC.visibility_of_element_located((By.XPATH, xpath)))
    
def wallet_submit():
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div/div[1]/div/div[2]/div/button[2]').click()

def borrow_more():
    #borrow moreのチェック
    elem_tulip_borrowmore = drvr.find_element(by=By.CLASS_NAME, value='jss16').click()
    #借入比率をクリア
    time.sleep(1)
    wait_visible('/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[4]/div/div[2]/div[2]/div[1]/div[3]/div/input')
    elem_input_to_borrow = drvr.find_element(by=By.CSS_SELECTOR, value='body > div:nth-child(6) > div > div.modal.fade.show > div > div > div.leverage-modal-meta.modal-body > section > div.leverage-modal__main-content > div.leverage-modal-meta__lev > div > div.leverage-modal-meta__lev-box__selector > div.dual-borrow-label > div:nth-child(1) > div:nth-child(3) > div > input').clear()
    #レバレッジ欄をクリア
    elem_tulip_3x = drvr.find_element(by=By.CSS_SELECTOR, value='body > div:nth-child(6) > div > div.modal.fade.show > div > div > div.leverage-modal-meta.modal-body > section > div.leverage-modal__main-content > div.leverage-modal-meta__lev > div > div.leverage-modal-meta__lev-box__input > div.customNumberInput > input').clear()
    time.sleep(0.5)
    #レバレッジを指定
    elem_tulip_3x = drvr.find_element(by=By.CSS_SELECTOR, value='body > div:nth-child(6) > div > div.modal.fade.show > div > div > div.leverage-modal-meta.modal-body > section > div.leverage-modal__main-content > div.leverage-modal-meta__lev > div > div.leverage-modal-meta__lev-box__input > div.customNumberInput > input').send_keys(3.0)
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
    borrow_usdc = float(elem_tulip_borrow_amount.split(' ')[4].replace('$','').replace(',',''))
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
#アラートの削除スクリプト
script = """
    elem_alert = document.getElementsByClassName("low-tps-warning")
    elem_alert = Array.from( elem_alert )
    elem_alert.forEach(elem_alert => elem_alert.remove())
"""
script_div = """
    elem_div = document.querySelector("body > div.szh-menu-container.szh-menu-container--itemTransition.community-menu")
    elem_div = Array.from( elem_div )
    elem_div.forEach(elem_div => elem_div.remove())
"""

EXTENSION_PATH = Extension_path
options = Options()
options.add_extension(EXTENSION_PATH)
options.binary_location = binary_location 
driver_path = driver_path
drvr = webdriver.Chrome(options = options, executable_path = driver_path)

#solana tplチェック
drvr.switch_to.window(drvr.window_handles[0])
site_tpl = "https://solanabeach.io"
drvr.get(site_tpl)
time.sleep(5)
elem_solana_tpl = float(drvr.find_element(by=By.XPATH, value='//*[@id="app"]/div[3]/div/div/div/div[6]/div/div[1]/div/div[1]/div/div/p/span').text.replace(',',''))


#tplが2000以上だと実行
if elem_solana_tpl >= 1000:
    site ="https://tulip.garden/vaults"

    drvr.get(site)
    drvr.execute_script(script)
    time.sleep(2)
    drvr.switch_to.window(drvr.window_handles[1])
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/div/div[2]/button[2]').click()
    time.sleep(1)
    wait_visible('//*[@id="root"]/main/div[2]/form/div/div/div[2]/div/textarea')
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/div/div/div[2]/div/textarea').send_keys(Seed_key)
    wait_visible('//*[@id="root"]/main/div[2]/form/button')
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/button').click()
    wait_visible('//*[@id="root"]/main/div[2]/form/div/div/div[2]/ul/li[1]')
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/button').click()
    wait_visible('//*[@id="root"]/main/div[2]/form/div/div/div[3]/p')
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/div/div/div[2]/input').send_keys(Wallet_pass)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/div/div/div[2]/div/div/input').send_keys(Wallet_pass)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/div/div/div[3]/span/input').click()
    wait_visible('//*[@id="root"]/main/div[2]/form/button')
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/button').click()
    wait_visible('//*[@id="root"]/main/div[2]/form/button')
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/main/div[2]/form/button').click()
    time.sleep(3)
    #tulipのタブに切り替え
    drvr.switch_to.window(drvr.window_handles[0])
    drvr.execute_script(script)
    wait_visible('//*[@id="root"]/div[1]/div[2]/div[1]/div[2]/div/div/button')
    #コネクトボタンクリック
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div[1]/div[2]/div[1]/div[2]/div/div/button').click()
    wait_visible('//*[@id="root"]/div[1]/div[2]/div[1]/div[2]/div/div/div/button[1]')
    #Phantomを選択
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div[1]/div[2]/div[1]/div[2]/div/div/div/button[1]').click()
    time.sleep(3)
    drvr.switch_to.window(drvr.window_handles[2])
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div/div[1]/div[2]/div/button[2]').click()
    time.sleep(3)
    drvr.switch_to.window(drvr.window_handles[0])
    drvr.execute_script(script)
    drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div[1]/div[1]/nav/ul/li[2]/a').click()
    time.sleep(1)
    if len(drvr.find_elements(by=By.CSS_SELECTOR, value='#root > div.app > div.app-body > div.infobar--error.infobar') )> 0 :
        send_line("REPAIR")
        drvr.find_element(by=By.XPATH, value='//*[@id="root"]/div[1]/div[2]/div[1]/button').click()
        time.sleep(2)
        drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/div/div[2]/div/div[2]/div/button').click()
        time.sleep(2)
        drvr.switch_to.window(drvr.window_handles[2])
        time.sleep(2)
        wallet_submit()
        time.sleep(60)
        drvr.quit()

    else:
        #jsonファイルを使って認証情報を取得
        scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
        c = ServiceAccountCredentials.from_json_keyfile_name(json_key, scope)

        #認証情報を使ってスプレッドシートの操作権を取得
        gs = gspread.authorize(c)

        SPREADSHEET_KEY = Spreadsheet_key
        worksheet = gs.open_by_key(SPREADSHEET_KEY).worksheet(sheet_name)
        workbook = gs.open_by_key(SPREADSHEET_KEY)
        worksheet = workbook.worksheet(sheet_name)

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
            profit = drvr.find_element(by = By.XPATH, value=f'//*[@id="root"]/div[1]/div[2]/div/div[{i}]/div/div[4]/div[2]/div[1]/div[2]/span').text.replace('+$','').replace('$','')
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
        sheetName = sheet_name
        sh = gs.open_by_key(Spreadsheet_key)
    #スプレッドシート更新の時間指定
    if datetime.datetime.now().hour == 14 or datetime.datetime.now().hour == 6 or datetime.datetime.now().hour == 0:
        sh.values_append(sheetName,
                         {'valueInputOption': 'USER_ENTERED'},
                         {'values': df.values.tolist()}
                         )
    drvr.switch_to.window(drvr.window_handles[0])
    drvr.execute_script(script)
    #killer bufferを基準に必要あればアジャスト
    rows = 1
    for i in range(0,len(item_lists)):
        rows += 1
        elem_tulip_killer_buffer = float(kills[i])
        drvr.execute_script(script)
        if elem_tulip_killer_buffer <= 17.5:
            drvr.find_element(by=By.XPATH, value=f'//*[@id="root"]/div[1]/div[2]/div/div[{i+2}]/div/div[7]/div[1]/button').click()
            drvr.set_window_size(990,900)
            time.sleep(1)
            #デポジット
            elem_tulip_input_usdc = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[2]/div[2]/div[2]/input').clear()
            time.sleep(0.5)
            elem_tulip_input_usdc = drvr.find_element(by=By.XPATH, value='/html/body/div[2]/div/div[1]/div/div/div[2]/section/div[1]/div[2]/div[2]/div[2]/input').send_keys(deposit_amount)
            time.sleep(1)
            borrow_more()
            time.sleep(1)
            send_line("DEPOSIT")
            #注文確定
            drvr.switch_to.window(drvr.window_handles[2])
            wallet_submit()
            time.sleep(90)
            drvr.set_window_size(1100,900)

        elif elem_tulip_killer_buffer >= 19:
            elem_tulip_coll = drvr.find_element(by=By.XPATH, value=f'//*[@id="root"]/div[1]/div[2]/div/div[{rows}]/div/div[7]/div[1]/button').click()
            drvr.execute_script(script_div)
            drvr.set_window_size(990,900)
            time.sleep(1)
            borrow_more()
            time.sleep(1)
            #注文確定
            drvr.switch_to.window(drvr.window_handles[2])
            time.sleep(2)
            wallet_submit()
            drvr.switch_to.window(drvr.window_handles[0])
            send_line("3x")
            time.sleep(90)
            drvr.set_window_size(1100,900)
    drvr.quit()
else:
#TPLが2000以下だとLINE通知
    send_line('TPL IS LOW')
    drvr.quit()

