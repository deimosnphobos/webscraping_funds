import requests
import pprint
import pandas as pd
import re
import numpy as np
from bs4 import BeautifulSoup
pd.set_option('display.max_colwidth', None)

""" Extracting MUTUAL FUNDS from the website"""
url_mf = 'https://akportfoy.com.tr/tr/node/yatirim_fonlari'
soup_mf = BeautifulSoup(requests.get(url_mf).content, 'html.parser')

"""Scraping the Mutual Fund webpage and listing the funds in a dictionary"""
akprtfy_fonlar = {}

fund_subtype_list = [1, 2, 3, 4, 5, 6, 9, 111, 11, 30,
                     32]  # These subtype numbers are found from inspecting the website code!

for x, fund_no in enumerate(fund_subtype_list):
    # APK'nin collapse_fundsubtype_ code, which is 12, is omitted
    href_ = '#collapse_fundsubtype_' + str(fund_no)
    title = ' '.join(soup_mf.find(href=href_).text.split('<')[0].split())
    varlik_kodu = title.split(' Fonlar')[0].split(' Yatırım')[0]

    varliklar = {}
    id_name = 'collapse_fundsubtype_' + str(fund_no)
    headlines = soup_mf.find(id=id_name)
    tagged_ = headlines.find_all('a', href=True)

    for x in tagged_:
        fon_kodu = x.text.split('<')[0].split(':')[0]
        fon_ismi = x.text.split('<')[0].split(':')[1].split('Ak Portföy ')[1]

        varliklar[fon_kodu] = fon_ismi

    akprtfy_fonlar[varlik_kodu] = varliklar

"""From dictionary to DataFrame"""

### Finding the number of rows in a df
fon_siniflari = []
n, m = 0, 0
for c, i in enumerate(akprtfy_fonlar):
    m = len(akprtfy_fonlar[i])
    fon_siniflari.extend([list(akprtfy_fonlar.keys())[c]] * m)
    n += m

fon_kodlari = [i for j in range(len(akprtfy_fonlar.values())) for i in list(akprtfy_fonlar.values())[j]]
fon_isimleri = [i for j in range(len(akprtfy_fonlar.values())) for i in list(list(akprtfy_fonlar.values())[j].values())]

yatirim_fonlari = pd.DataFrame(data=np.zeros(shape=(n, 3)), columns=['Fon_Sinifi', 'Fon_Kodu', 'Fon_Ismi'])

yatirim_fonlari.iloc[:, 0] = fon_siniflari
yatirim_fonlari.iloc[:, 1] = fon_kodlari
yatirim_fonlari.iloc[:, 2] = fon_isimleri

yatirim_fonlari.set_index('Fon_Kodu', inplace=True)


""" Extracting PENSION FUNDS from the website"""
url_ef = 'https://akportfoy.com.tr/tr/node/avivasa_emeklilik'
soup_ef = BeautifulSoup(requests.get(url_ef).content, 'html.parser')

"""Scraping the Pension Fund webpage and listing the funds in a dictionary"""
akprtfy_fonlar_e = {}

fund_subtype_list_e = [1, 2, 3, 4, 5, 6, 7, 91, 92]  # These subtype numbers are found from inspecting the website code!

for x, i in enumerate(fund_subtype_list_e):
    href_ = '#collapse_fundsubtype_' + str(i)
    title = ' '.join(soup_ef.find(href=href_).text.split('<')[0].split())
    varlik_kodu = title.split(' Fonlar')[0].split(' Yatırım')[0]

    varliklar = {}
    id_name = 'collapse_fundsubtype_' + str(i)
    headlines = soup_ef.find(id=id_name)
    tagged_ = headlines.find_all('a', href=True)

    for x in tagged_:
        fon_kodu = x.text.split('<')[0].split(':')[0]
        fon_ismi = x.text.split('<')[0].split(':')[1].split('Hayat ')[1]
        varliklar[fon_kodu] = fon_ismi

    akprtfy_fonlar_e[varlik_kodu] = varliklar

"""From dictionary to DataFrame"""

### Finding the number of rows in a df
fon_siniflari_e = []
n, m = 0, 0
for c, i in enumerate(akprtfy_fonlar_e):
    m = len(akprtfy_fonlar_e[i])
    fon_siniflari_e.extend([list(akprtfy_fonlar_e.keys())[c]] * m)
    n += m

fon_kodlari_e = [i for j in range(len(akprtfy_fonlar_e.values())) for i in list(akprtfy_fonlar_e.values())[j]]
fon_isimleri_e = [i for j in range(len(akprtfy_fonlar_e.values())) for i in
                  list(list(akprtfy_fonlar_e.values())[j].values())]

emeklilik_fonlari = pd.DataFrame(data=np.zeros(shape=(n, 3)), columns=['Fon_Sinifi', 'Fon_Kodu', 'Fon_Ismi'])

emeklilik_fonlari.iloc[:, 0] = fon_siniflari_e
emeklilik_fonlari.iloc[:, 1] = fon_kodlari_e
emeklilik_fonlari.iloc[:, 2] = fon_isimleri_e

emeklilik_fonlari.set_index('Fon_Kodu', inplace=True)


## Finding and adding each MUTUAL FUND's detail into dataframe
mutual_fund_lst = {}

for i in range(len(yatirim_fonlari.index)):
    fund_name = yatirim_fonlari.index[i]

    url = 'https://akportfoy.com.tr/tr/fund/' + fund_name
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="collapse_fundinfo")

    fund_labels = results.find_all('th')
    label_values = results.find_all('td')

    try:
        fon_kodu = results.find('p').text.split(' - ')[1]
        fon_ismi = results.find('p').text.split(' - ')[0]
    except AttributeError:
        continue

    ### Finding Fund Asset Distribution ###
    fund_contents = soup.find(class_="wrap-images")
    assets = {}
    ratio = 0
    txt = ''
    for x in fund_contents.prettify().split('"v":'):
        if x[0] == '"':
            txt = x[0:x.find('},{')]
        if x[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            ratio = np.round(eval(x[0:x.find('}]')]), 2)
        assets[txt] = ratio

    assets = dict(sorted(assets.items(), key=lambda item: item[1], reverse=True))
    #########

    fon_dict = {}
    for i in range(len(fund_labels)):
        fon_dict[fund_labels[i].text] = label_values[i].text

    fon_dict['Fon Varlık Dağılımı'] = assets
    fund_info = list(fon_dict.values())

    mutual_fund_lst[fund_name] = fund_info

# Structuring the dataframe
mutual_fund_df = pd.DataFrame(data=mutual_fund_lst).T
mutual_fund_df.columns = fon_dict.keys()
mutual_fund_df = mutual_fund_df[
    ['Karşılaştırma Ölçütü', 'Fon Büyüklüğü TL', 'Yönetim Ücreti (Yıllık Yüzde)', 'Fon Varlık Dağılımı', 'Risk Değeri',
     'Önerilen Vade']]
mutual_fund_df.index.name = 'Fon_Kodu'

mutualfunds = yatirim_fonlari.join(mutual_fund_df, on='Fon_Kodu')
#mutualfunds.style.set_properties(**{'text-align': 'left'})

## Finding and adding each PENSION FUND's detail into dataframe
pension_fund_lst = {}

for i in range(len(emeklilik_fonlari.index)):
    fund_name = emeklilik_fonlari.index[i]

    url = 'https://akportfoy.com.tr/tr/fund/' + fund_name
    page = requests.get(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id="collapse_fundinfo")

    fund_labels = results.find_all('th')
    label_values = results.find_all('td')

    try:
        fon_kodu = results.find('p').text.split(' - ')[1]
        fon_ismi = results.find('p').text.split(' - ')[0]
    except AttributeError:
        continue

    ### Finding Fund Asset Distribution ###
    fund_contents = soup.find(class_="wrap-images")
    assets = {}
    ratio = 0
    for x in fund_contents.prettify().split('"v":'):
        if x[0] == '"':
            txt = x[0:x.find('},{')]
        if x[0] in ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']:
            ratio = np.round(eval(x[0:x.find('}]')]), 2)
        assets[txt] = ratio

    assets = dict(sorted(assets.items(), key=lambda item: item[1], reverse=True))
    #########

    fon_dict = {}
    for i in range(len(fund_labels)):
        fon_dict[fund_labels[i].text] = label_values[i].text

    fon_dict['Fon Varlık Dağılımı'] = assets
    fund_info = list(fon_dict.values())

    pension_fund_lst[fund_name] = fund_info

# Structuring the dataframe
pension_fund_df = pd.DataFrame(data=pension_fund_lst).T
pension_fund_df.columns = fon_dict.keys()
pension_fund_df = pension_fund_df[
    ['Karşılaştırma Ölçütü', 'Fon Büyüklüğü TL', 'Yönetim Ücreti (Yıllık Yüzde)', 'Fon Varlık Dağılımı', 'Risk Değeri',
     'Önerilen Vade']]
pension_fund_df.index.name = 'Fon_Kodu'

# with pd.ExcelWriter('funds.xlsx') as writer:
#     mutualfunds.to_excel(writer, sheet_name='Mutual Funds')
#     pensionfunds.to_excel(writer, sheet_name='Pension Funds')