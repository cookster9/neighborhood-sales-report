import requests
from lxml import html
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import os
from dashboard.models import RealEstateProperties
from dashboard.models import Neighborhoods
from dashboard.models import RealEstateSales
import datetime

import pdb

url_base = 'https://davidson-tn-citizen.comper.info/template.aspx?propertyID='
def update_neighborhood(id):
    print("in update neighborhood")
    neighborhood_id = id
    # get map parcel of top 1 reis in neighborhood https://stackoverflow.com/questions/844591/how-to-do-select-max-in-django
    # trim map parcel
    # e.g. 07116007400
    n = Neighborhoods.objects\
        .filter(id=neighborhood_id
                ,status='pending')
    if(len(n)>0):
        n[0].status = 'processing'
        print("set processing?")
        n[0].save()
    else:
        return 'ID already processing'

    houses_to_try_urls_for = RealEstateSales.objects\
        .select_related('real_estate_properties')\
        .filter(real_estate_properties__property_use='SINGLE FAMILY'
                ,real_estate_properties__neighborhoods_id=neighborhood_id) \
        .order_by('-sale_date')
    for house in houses_to_try_urls_for:
        trimmed_map_parcel = house.real_estate_properties.map_parcel_trimmed
        # trimmed_map_parcel = '07116007400'

        url = url_base+trimmed_map_parcel
        # go through all sales on comper site
        for j in range(10):
            try:
                print("Trying url",url)

                a = get_html(url)
                # a = example_html

                soup = BeautifulSoup(str(a),'lxml')

                subjectBox = soup.find('div', class_='subjectBox')
                if subjectBox != None:
                    # subjectBoxSoup = BeautifulSoup(subjectBox,'lxml')
                    salesList = soup.find_all('li', class_='comp')
                    for comp in salesList:
                        map_parcel = comp['data-id']
                        sale_date = comp['saledate']
                        sale_price = comp['saleprice']
                        address = comp.find_all('div')[1].find_all('h2')[0].string
                        print(address)
                        print("sale date comparison")
                        print(map_parcel)
                        print(sale_date)
                        sale_date_obj = datetime.datetime.strptime(sale_date, '%d %b %Y').date()
                        print(sale_date_obj)
                        houses_in_db = RealEstateProperties.objects \
                            .filter(map_parcel_trimmed=map_parcel)
                        houses_returned=len(houses_in_db)
                        if houses_returned == 0:
                            print("need to create new property as well")
                            house_in_db = RealEstateProperties.objects.create(map_parcel_trimmed=map_parcel
                                                                              ,location=address
                                                                              ,neighborhood=neighborhood_id
                                                                              ,last_update_date=datetime.date.today())
                        else:
                            house_in_db = houses_in_db[0]
                        print("got house",house_in_db)
                        latest_sale = RealEstateSales.objects \
                            .filter(real_estate_properties_id=house_in_db.id) \
                            .order_by('-sale_date')
                        print("got sale", latest_sale)
                        print(latest_sale)
                        num_sales=len(latest_sale)
                        if num_sales == 0:
                            print("add sale")
                            sale_create = RealEstateSales.objects.create(sale_date=sale_date_obj
                                                                         ,sale_price=sale_price
                                                                         ,real_estate_properties_id=house_in_db.id)
                        else:
                            if latest_sale[0].sale_date < sale_date_obj:
                                print("add sale")
                                sale_create = RealEstateSales.objects.create(sale_date=sale_date_obj
                                                                             , sale_price=sale_price
                                                                             , real_estate_properties_id=house_in_db.id)

                    n[0].status = 'pending'
                    n[0].save()
                    #SUCCESS
                    return 'Update queued for neighborhood: ' + str(id)
            except Exception as e:
                print(e)
                print("Waiting to try again")
                sleep(60)
            else:
                # print(get_response.status_code)
                # print(contents.content)

                return 0


    return 'Could not update neighborhood'+str(id)

def get_html(url):
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--allow-running-insecure-content')
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    # executable_path param is not needed if you updated PATH
    PROJECT_ROOT = '/Users/andrewcook/Documents/Programming/'
    DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")
    browser = webdriver.Chrome(options=options)

    print("about to get url")
    browser.get(url)

    # elem = myProperty.click()
    # browser.execute_script("arguments[0].click();", myProperty)
    print("getting html")
    html = browser.page_source

    return html
example_html = """<div id="myPropertyInfo" style="padding:10px;"><div class="subjectBox" data-id="07116007400" style="cursor:pointer"><div style="float:left; width:80px;"> <img id="img-07116007400" src="proxy2.php?csurl=http://www.padctn.org/prc/Image_2023_Sep/48000/596001.JPG" style="width:80px;"/></div><div style="float:left; width:360px; margin-bottom:5px;"> <h2 style="float:left; padding-left:0.5em; text-transform: capitalize;">1311 rosedale ave</h2></div><div style="float:left; width:380px;"> <div style="margin-left:10px; margin-bottom:10px;"><ul class="propertyInfoC1" style="float:left; overflow: hidden; padding-right:1em; color:#444;"><li title="N/A">Distance: N/A</li><li title="N/A">Sale Date: N/A</li><li title="$296.84">App.Value/SqFt: $296.84</li> </ul><ul class="propertyInfoC2" style="float:left; overflow: hidden; padding-right:1em; color:#444;"><li title="1,075">Living Area: 1,075</li><li title="SINGLE FAMILY">Property Type: SINGLE FAMILY</li><li title="TOM JOY">Neigborhood: TOM JOY</li> </ul> </div></div><div style="clear:both;"></div></div></div>
<div class="subjectBox" data-id="07116007400" style="cursor:pointer"><div style="float:left; width:80px;"> <img id="img-07116007400" src="proxy2.php?csurl=http://www.padctn.org/prc/Image_2023_Sep/48000/596001.JPG" style="width:80px;"/></div><div style="float:left; width:360px; margin-bottom:5px;"> <h2 style="float:left; padding-left:0.5em; text-transform: capitalize;">1311 rosedale ave</h2></div><div style="float:left; width:380px;"> <div style="margin-left:10px; margin-bottom:10px;"><ul class="propertyInfoC1" style="float:left; overflow: hidden; padding-right:1em; color:#444;"><li title="N/A">Distance: N/A</li><li title="N/A">Sale Date: N/A</li><li title="$296.84">App.Value/SqFt: $296.84</li> </ul><ul class="propertyInfoC2" style="float:left; overflow: hidden; padding-right:1em; color:#444;"><li title="1,075">Living Area: 1,075</li><li title="SINGLE FAMILY">Property Type: SINGLE FAMILY</li><li title="TOM JOY">Neigborhood: TOM JOY</li> </ul> </div></div><div style="clear:both;"></div></div>
"""