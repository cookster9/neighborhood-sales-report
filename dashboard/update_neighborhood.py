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

url_base = 'https://davidson-tn-citizen.comper.info/template.aspx?propertyID='
def update_neighborhood(id):
    print("in update neighborhood")
    # get map parcel of top 1 reis in neighborhood https://stackoverflow.com/questions/844591/how-to-do-select-max-in-django
    # trim map parcel
    # e.g. 07116007400
    n = Neighborhoods.objects\
        .filter(id=id
                ,status='pending')
    if(len(n)>0):
        n[0].status = 'processing'
        print("set processing?")
        n[0].save()
    else:
        return 'ID already processing'
    q = RealEstateSales.objects\
        .select_related('real_estate_properties')\
        .filter(real_estate_properties__property_use='SINGLE FAMILY'
                ,real_estate_properties__neighborhoods_id=id) \
        .order_by('-sale_date')
    for house in q:
        trimmed_map_parcel = q[0].map_parcel_trimmed
        # trimmed_map_parcel = '07116007400'

        url = url_base+trimmed_map_parcel
        # go through all sales on comper site
        for j in range(10):
            try:
                print("Trying url",url)
                # get_response = requests.get(url)
                # tree = html.fromstring(get_response.content)
                # sales_list_xpath = '/html/body/div[5]/div[2]/div[4]/ul'
                # sales_comps_xpath = '/html/body/div[5]/div[2]/div[4]/ul/li[1]'
                # sales_list = tree.xpath(sales_comps_xpath)
                # print(sales_list)


                a = get_html(url)
                # a = example_html
                soup = BeautifulSoup(a,'lxml')
                print(soup)
                subjectBox = soup.find('div', class_='subjectBox')
                if subjectBox != None:
                    # subjectBoxSoup = BeautifulSoup(subjectBox,'lxml')
                    map_parcel = subjectBox['data-id']
                    print(map_parcel)
                    mailing_address = subjectBox.h2.string
                    print(mailing_address)
                    sale_date = '//*[@id="propertyOverview"]/div[4]/ul/li[6]/text()'
                    sale_price = '//*[@id="propertyOverview"]/div[4]/ul/li[7]/text()'
                    property_use = '//*[@id="content"]/div/div[4]/div[1]/ul/li[7]/text()'
                    sq_ft = '//*[@id="content"]/div/div[4]/div[2]/div/div[1]/ul/li[3]/text()'
                    zone = '//*[@id="content"]/div/div[4]/div[1]/ul/li[8]/text()'
                    neighborhood = '//*[@id="content"]/div/div[4]/div[1]/ul/li[9]/text()'
                    location = '//*[@id="propertyOverview"]/ul/li[2]/text()'

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
    # executable_path param is not needed if you updated PATH
    PROJECT_ROOT = '/Users/andrewcook/Documents/Programming/'
    DRIVER_BIN = os.path.join(PROJECT_ROOT, "chromedriver")
    browser = webdriver.Chrome(options=options)

    browser.get(url)

    myProperty = browser.find_element(By.XPATH,"/html/body/div[5]/div[2]/div[2]/div[5]/div")
    print(myProperty)
    # elem = myProperty.click()
    browser.execute_script("arguments[0].click();", myProperty)
    html = browser.page_source
    soup = BeautifulSoup(html, 'lxml')
    # a = soup.find_all('li', class_='comp') # class_='class_name'

    a = soup.find('div', id='myPropertyInfo')  # just the one
    return a
example_html = """<div id="myPropertyInfo" style="padding:10px;"><div class="subjectBox" data-id="07116007400" style="cursor:pointer"><div style="float:left; width:80px;"> <img id="img-07116007400" src="proxy2.php?csurl=http://www.padctn.org/prc/Image_2023_Sep/48000/596001.JPG" style="width:80px;"/></div><div style="float:left; width:360px; margin-bottom:5px;"> <h2 style="float:left; padding-left:0.5em; text-transform: capitalize;">1311 rosedale ave</h2></div><div style="float:left; width:380px;"> <div style="margin-left:10px; margin-bottom:10px;"><ul class="propertyInfoC1" style="float:left; overflow: hidden; padding-right:1em; color:#444;"><li title="N/A">Distance: N/A</li><li title="N/A">Sale Date: N/A</li><li title="$296.84">App.Value/SqFt: $296.84</li> </ul><ul class="propertyInfoC2" style="float:left; overflow: hidden; padding-right:1em; color:#444;"><li title="1,075">Living Area: 1,075</li><li title="SINGLE FAMILY">Property Type: SINGLE FAMILY</li><li title="TOM JOY">Neigborhood: TOM JOY</li> </ul> </div></div><div style="clear:both;"></div></div></div>
<div class="subjectBox" data-id="07116007400" style="cursor:pointer"><div style="float:left; width:80px;"> <img id="img-07116007400" src="proxy2.php?csurl=http://www.padctn.org/prc/Image_2023_Sep/48000/596001.JPG" style="width:80px;"/></div><div style="float:left; width:360px; margin-bottom:5px;"> <h2 style="float:left; padding-left:0.5em; text-transform: capitalize;">1311 rosedale ave</h2></div><div style="float:left; width:380px;"> <div style="margin-left:10px; margin-bottom:10px;"><ul class="propertyInfoC1" style="float:left; overflow: hidden; padding-right:1em; color:#444;"><li title="N/A">Distance: N/A</li><li title="N/A">Sale Date: N/A</li><li title="$296.84">App.Value/SqFt: $296.84</li> </ul><ul class="propertyInfoC2" style="float:left; overflow: hidden; padding-right:1em; color:#444;"><li title="1,075">Living Area: 1,075</li><li title="SINGLE FAMILY">Property Type: SINGLE FAMILY</li><li title="TOM JOY">Neigborhood: TOM JOY</li> </ul> </div></div><div style="clear:both;"></div></div>
"""