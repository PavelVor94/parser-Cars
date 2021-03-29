from selenium import webdriver
import time
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from pandas import DataFrame

options = webdriver.ChromeOptions()
#options.add_argument("--headless")
driver = webdriver.Chrome(chrome_options=options)

def menu_click(menu : int, option : int):
    buts_down = driver.find_elements_by_xpath('//div[contains(@class,"react-select__dropdown-indicator")]')
    buts_down[menu].click()
    menu_one = driver.find_elements_by_xpath('//div[contains(@class,"react-select__menu")]')
    menu_one_options = driver.find_elements_by_xpath('//div[contains(@class,"react-select__option")]')
    count_options = len(menu_one_options)
    print(count_options)
    label = menu_one_options[option].text
    menu_one_options[option].click()
    time.sleep(0.8)
    return label , count_options

def forward_click(number : int):
    time.sleep(0.8)
    divs = driver.find_element_by_xpath('//div[@class="bulp-panel"]')
    menu_four_options = driver.find_elements_by_xpath('//*[@id="collapsible-panel--body"]/div/div/div/div[1]/div/div[1]/li')
    count_options = len(menu_four_options)
    label = menu_four_options[number].text
    menu_four_options[number].click()
    time.sleep(0.7)
    return label, count_options

def get_technology():
    try:
        edit_btn = driver.find_elements_by_xpath('//div[contains(@class,"accordion-icon ms-icon_edit")]')
        edit_btn[2].click()
    except:
        pass
    time.sleep(1)
    list_techonolgy = driver.find_elements_by_xpath('//li[contains(@class,"noteList technology-card")]')
    return list_techonolgy

def back():
    driver.execute_script("scrollBy(0,-100);")
    edit_btn = driver.find_elements_by_xpath('//div[contains(@class,"accordion-icon ms-icon_edit")]')
    edit_btn[0].click()
    time.sleep(0.8)

def back_forward():
    edit_btn = driver.find_elements_by_xpath('//div[contains(@class,"accordion-icon ms-icon_edit")]')
    edit_btn[1].click()
    time.sleep(0.8)

def get_type():
    edit_btn = driver.find_elements_by_xpath('//div[contains(@class,"accordion-icon ms-icon_edit")]')
    edit_btn[0].click()
    time.sleep(0.8)
    typ = driver.find_elements_by_xpath('//div[contains(@class,"react-select__single-value--is-disabled")]')[0].text
    edit_btn = driver.find_elements_by_xpath('//div[contains(@class,"accordion-icon ms-icon_edit")]')
    edit_btn[0].click()
    time.sleep(0.8)
    return typ


driver.get("https://www.osram.co.uk/apps/gvlrg/en_GB")
time.sleep(2)
driver.find_element_by_xpath('//button[contains(@id, "accept-btn")]').click()
time.sleep(2)
driver.find_element_by_xpath('//div[@class="vehicle"]/button').click()
time.sleep(2)

list_result = []

count_brands = 0
brand_name, brand_len = menu_click(0,0)
dicts = dict()
while count_brands < brand_len:
    count_years = 0
    year_name, year_len = menu_click(1,count_years)
    while count_years < year_len:
        count_model = 0
        model_name, model_len = menu_click(2, count_model)
        try:
            edi = driver.find_elements_by_xpath('//div[contains(@class,"accordion-icon ms-icon_edit")]')
        except:
            edi = None
        if edi:
            type_name = get_type()
        while count_model < model_len:

            try:
                count_forward = 0
                forward_name, forward_len = forward_click(count_forward)
                while count_forward < forward_len:
                    count_forward += 1
                    count_techonology = 1
                    dicts['BRAND'] = brand_name
                    dicts['MANUFACTURER YEAR'] = year_name
                    dicts['MODEL'] = model_name
                    dicts['TYPE'] = type_name
                    dicts['POSITION'] = forward_name
                    for i in get_technology():
                        dicts['TECHNOLOGY '+str(count_techonology)] = i.text
                        count_techonology+=1
                    list_result.append(dicts)
                    if len(list_result) % 50 == 0 : DataFrame(list_result).to_excel('./result.xlsx' , index=False)
                    print(len(list_result))
                    dicts = dict()
                    back_forward()
                    if count_forward >= forward_len: break
                    forward_name= forward_click(count_forward)[0]
            except NoSuchElementException:
                count_types = 0
                type_name , type_len = menu_click(3,count_types)
                while count_types < type_len:
                    count_forward = 0
                    forward_name, forward_len = forward_click(count_forward)
                    while count_forward < forward_len:
                        count_forward += 1
                        count_techonology = 1
                        dicts['BRAND'] = brand_name
                        dicts['MANUFACTURER YEAR'] = year_name
                        dicts['MODEL'] = model_name
                        dicts['TYPE'] = type_name
                        dicts['POSITION'] = forward_name
                        for i in get_technology():
                            dicts['TECHNOLOGY '+str(count_techonology)] = i.text
                            count_techonology+=1
                        list_result.append(dicts)
                        if len(list_result) % 50 == 0 : DataFrame(list_result).to_excel('./result.xlsx' , index=False)
                        print(len(list_result))
                        dicts = dict()
                        back_forward()
                        if count_forward >= forward_len: break
                        forward_name= forward_click(count_forward)[0]
                    count_types+=1
                    if count_types >= type_len: break
                    back()
                    type_name = menu_click(3, count_types)[0]
            count_model+=1
            if count_model >= model_len : break
            back()
            model_name = menu_click(2, count_model)[0]
        count_years+=1
        if count_years >= year_len: break
        back()
        year_name= menu_click(1, count_years)[0]
    count_brands+=1
    dicts = dict()
    if count_brands >= brand_len: break
    back()
    brand_name = menu_click(0,count_brands)[0]
DataFrame(list_result).to_excel('./result.xlsx' , index=False)



