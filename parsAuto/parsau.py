import requests
from pandas import DataFrame
import time
import sys

URL_YEARS = 'https://api-vlrg.osram.info/cars/lookups?lookuptype=years&lang=gb&manufacturer_id=' # +id brand
URL_MODELS = 'https://api-vlrg.osram.info/cars/lookupmodelvariant?kind_id=1&lookuptype=models&lang=gb&manufacturer_id=927&constructionyear=' #+ year
URL_TYPES = 'https://api-vlrg.osram.info/cars/lookuptypeinfo?lang=gb&variant_id=VARIANTID&model_id=MODELID&constructionyear=' #+ year  replace VARIANTID MODELID
URL_POSITIONS = 'https://api-vlrg.osram.info/bulbs/positions?car_id=TYPEID&lang=gb' # replace TYPEID
URL_TECHNOLOGY ='https://api-vlrg.osram.info/bulbs/technologies?car_id=TYPEID&use_id=USEID&lang=gb' # replace TYPEID USEID
URL_PRODUCTS = 'https://api-vlrg.osram.info/bulbs/pillars?car_id=TYPEID&use_id=USEID&technology_id=TECHNOLOGYID&lang=gb' # replace TYPEID USEID TECHNOLOGYID
URL_INFO = 'https://api-vlrg.osram.info/bulbs/product_info?ean=PRODUCTID&lang=gb' # replace PRODUCTID

STEP = 100

list_result = []
start = time.time()

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
        }

def load_main():
    brands = requests.get('https://api-vlrg.osram.info/cars/lookups?kind_id=1&lang=gb&lookuptype=manufacturers', headers=HEADERS).json()
    for brand in brands:
        try:
            load_years(URL_YEARS+brand['id'], {"BRAND_NAME": brand['name']})
        except:
            print('Failed brand' , brand['name'])
            print(sys.exc_info())
    DataFrame(list_result).to_excel('./result.xlsx' , ';' , index=False)

def load_years(url, data_r : dict):
    data = data_r
    years = requests.get(url, headers=HEADERS).json()
    for year in years:
        data['YEAR'] = year['name']
        data['YEAR_ID'] = year['id']
        try:
            load_models(URL_MODELS+year['id'], data)
        except:
            print('Failed year' , year['name'])
            print(sys.exc_info())

def load_models(url, data_r : dict):
    data = data_r
    models = requests.get(url, headers=HEADERS).json()
    for model in models:
        data['MODEL_NAME'] = model['model_name']
        data['VARIANT_NAME'] = model['variant_name']
        try:
            load_types(URL_TYPES.replace('VARIANTID' , model['variant_id']).replace('MODELID' , model['model_id'])+data['YEAR_ID'], data)
        except:
            print('Failed model' , model['model_name'])
            print(sys.exc_info())

def load_types(url, data_r : dict):
    data = data_r
    types = requests.get(url, headers=HEADERS).json()
    for type in types:
        data['MODEL_TYPE'] = type['model_type']
        data['TYPE_NAME'] = type['name']
        data['TYPE_ID'] = type['id']
        data['TYPE_KW'] = type['type_kw']
        data['TYPE_FROM'] = type['type_from']
        data['TYPE_TO'] = type['type_to']
        try:
            load_positions(URL_POSITIONS.replace('TYPEID' , data['TYPE_ID']), data)
        except:
            print('Failed type' , type['name'])
            print(sys.exc_info())


def load_positions(url, data_r : dict):
    data = data_r
    positions = requests.get(url, headers=HEADERS).json()
    first = False
    for position in positions:
        if position['pos_name'] != 'Front light sources': continue
        data['POSITION_ID'] = position['pos_id']
        data['USE_ID'] = position['use_id']
        data['POSITION_NAME'] = position['use_name']
        try:
            load_technology(URL_TECHNOLOGY.replace('TYPEID' , data['TYPE_ID']).replace('USEID' , data['USE_ID']), data, first)
            first = True
        except:
            print('Failed position' , position['use_name'])
            print(sys.exc_info())

def load_technology(url, data_r : dict, first):
    try:
        data = data_r
        technologyes = requests.get(url, headers=HEADERS).json()
        result_dict = dict()
        if first:
            result_dict['BRAND'] = ''
            result_dict['MANUFACTURER YEAR'] = ''
            result_dict['MODEL'] = ''
            result_dict['TYPE'] = ''
        else:
            result_dict['BRAND'] = data['BRAND_NAME']
            result_dict['MANUFACTURER YEAR'] = data['YEAR']
            result_dict['MODEL'] = data['MODEL_NAME'] + ' - ' + data['VARIANT_NAME']
            result_dict['TYPE'] = data['TYPE_NAME']+ ' '+ data['TYPE_KW'] + ' (' + data['TYPE_FROM'][:4]+'.'+data['TYPE_FROM'][4:] + '-' + data['TYPE_TO'] + ')'
        result_dict['POSITION'] = data['POSITION_NAME']
        for i,technology in enumerate(technologyes, start=1):
            product = requests.get(URL_PRODUCTS.replace('TYPEID' , data['TYPE_ID']).replace('USEID' , data['USE_ID']).replace('TECHNOLOGYID' , technology['technology_id']), headers=HEADERS).json()[0]
            info = requests.get(URL_INFO.replace('PRODUCTID' , product['ean']), headers=HEADERS).json()
            result_dict['ECE CATEGORY '+str(i)] = info['oece'].replace('&nbsp;' , '')
            result_dict['TECH_DATA '+str(i)] = info['linfo']
            result_dict['TECHNOLOGY '+str(i)] = technology['tech_name']
        list_result.append(result_dict)
        if len(list_result) % STEP == 0: DataFrame(list_result).to_excel('./result.xlsx' , ';' , index=False)
        print(len(list_result))
    except:
        print('Failed technology')
        print(sys.exc_info())




load_main()