import scrapy
import json
import requests
from pandas import DataFrame
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36"
        }

class PasraSpider(scrapy.Spider):
    name = 'pasrA'
    start_urls = ['https://api-vlrg.osram.info/cars/lookups?kind_id=1&lang=gb&lookuptype=manufacturers']
    URL_YEARS = 'https://api-vlrg.osram.info/cars/lookups?lookuptype=years&lang=gb&manufacturer_id=' # +id brand
    URL_MODELS = 'https://api-vlrg.osram.info/cars/lookupmodelvariant?kind_id=1&lookuptype=models&lang=gb&manufacturer_id=927&constructionyear=' #+ year
    URL_TYPES = 'https://api-vlrg.osram.info/cars/lookuptypeinfo?lang=gb&variant_id=VARIANTID&model_id=MODELID&constructionyear=' #+ year  replace VARIANTID MODELID
    URL_POSITIONS = 'https://api-vlrg.osram.info/bulbs/positions?car_id=TYPEID&lang=gb' # replace TYPEID
    URL_TECHNOLOGY ='https://api-vlrg.osram.info/bulbs/technologies?car_id=TYPEID&use_id=USEID&lang=gb' # replace TYPEID USEID
    URL_PRODUCTS = 'https://api-vlrg.osram.info/bulbs/pillars?car_id=TYPEID&use_id=USEID&technology_id=TECHNOLOGYID&lang=gb' # replace TYPEID USEID TECHNOLOGYID
    URL_INFO = 'https://api-vlrg.osram.info/bulbs/product_info?ean=PRODUCTID&lang=gb' # replace PRODUCTID

    STEP = 10

    list_result = []
    start = time.time()

    def parse(self, response):
        brands = json.loads(response.text)
        for brand in brands:
            yield  scrapy.Request(self.URL_YEARS+brand['id'], callback=self.load_years, meta={"BRAND_NAME": brand['name']})

    def load_years(self, response):
        years = json.loads(response.text)
        data = response.meta
        for year in years:
            data['YEAR'] = year['name']
            data['YEAR_ID'] = year['id']
            yield  scrapy.Request(self.URL_MODELS+year['id'], callback=self.load_models, meta=data)

    def load_models(self,response):
        models = json.loads(response.text)
        data = response.meta
        for model in models:
            data['MODEL_NAME'] = model['model_name']
            data['VARIANT_NAME'] = model['variant_name']
            yield  scrapy.Request(self.URL_TYPES.replace('VARIANTID' , model['variant_id']).replace('MODELID' , model['model_id'])+data['YEAR_ID'], callback=self.load_types, meta=data)


    def load_types(self, response):
        types = json.loads(response.text)
        data = response.meta
        for type in types:
            data['MODEL_TYPE'] = type['model_type']
            data['TYPE_NAME'] = type['name']
            data['TYPE_ID'] = type['id']
            data['TYPE_KW'] = type['type_kw']
            data['TYPE_FROM'] = type['type_from']
            data['TYPE_TO'] = type['type_to']
            yield  scrapy.Request(self.URL_POSITIONS.replace('TYPEID' , data['TYPE_ID']), callback=self.load_positions, meta=data)

    def load_positions(self, response):
        positions = json.loads(response.text)
        data = response.meta
        for position in positions:
            if position['pos_name'] != 'Front light sources': continue
            data['POSITION_ID'] = position['pos_id']
            data['USE_ID'] = position['use_id']
            data['POSITION_NAME'] = position['use_name']
            yield  scrapy.Request(self.URL_TECHNOLOGY.replace('TYPEID' , data['TYPE_ID']).replace('USEID' , data['USE_ID']), callback=self.load_technologys, meta=data)

    def load_technologys(self, response):
        technologys = json.loads(response.text)
        data = response.meta
        result_dict = dict()
        result_dict['BRAND'] = data['BRAND_NAME']
        result_dict['MANUFACTURER YEAR'] = data['YEAR']
        result_dict['MODEL'] = data['MODEL_NAME'] + ' - ' + data['VARIANT_NAME']
        result_dict['TYPE'] = data['TYPE_NAME']+ ' '+ data['TYPE_KW'] + ' (' + data['TYPE_FROM'] + '-' + data['TYPE_TO'] + ')'
        result_dict['POSITION'] = data['POSITION_NAME']
        for i,technology in enumerate(technologys, start=1):
            product = requests.get(self.URL_PRODUCTS.replace('TYPEID' , data['TYPE_ID']).replace('USEID' , data['USE_ID']).replace('TECHNOLOGYID' , technology['technology_id']), headers=HEADERS).json()[0]
            info = requests.get(self.URL_INFO.replace('PRODUCTID' , product['ean']), headers=HEADERS).json()
            result_dict['ECE CATEGORY '+str(i)] = info['oece']
            result_dict['TECH_DATA '+str(i)] = info['linfo']
            result_dict['TECHNOLOGY '+str(i)] = technology['tech_name']
        self.list_result.append(result_dict)
        if len(self.list_result) % self.STEP == 0: DataFrame(self.list_result).to_excel('./result.xlsx' , ';' , index=False)
        print(len(self.list_result))

    def closed(self, reason):
        DataFrame(self.list_result).to_excel('./result.xlsx' , ';' , index=False)
        print(time.time()-self.start)
