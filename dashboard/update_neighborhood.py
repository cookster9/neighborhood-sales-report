import requests
from lxml import html
from time import sleep
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
        print("Trying url",url)

        try:
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
                    property_type = comp['buildingtype']
                    sq_ft = comp['finishedarea']
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
                        # try again...
                        houses_in_db = RealEstateProperties.objects \
                            .filter(location=address
                                    ,neighborhoods_id=neighborhood_id)
                        houses_returned = len(houses_in_db)
                        if houses_returned != 1:
                            print("need to create new property as well")
                            tn_address_id = get_address_id(address, n[0].latitude, n[0].longitude)
                            house_in_db = RealEstateProperties.objects.create(map_parcel_trimmed=map_parcel
                                                                              ,location=address
                                                                              ,neighborhoods_id=neighborhood_id
                                                                              ,last_update_date=datetime.date.today()
                                                                              ,property_use=property_type
                                                                              ,tn_davidson_addresses_id=tn_address_id
                                                                              ,square_footage=sq_ft)
                        else:
                            house_in_db = houses_in_db[0]
                            #update parcel to what's on comp website
                            house_in_db.map_parcel_trimmed=map_parcel
                            # may have gone from vacant to single family
                            house_in_db.property_use=property_type
                            house_in_db.last_update_date = datetime.date.today()
                            house_in_db.save()
                    else:
                        house_in_db = houses_in_db[0]
                        # update parcel to what's on comp website
                        house_in_db.map_parcel_trimmed = map_parcel
                        # may have gone from vacant to single family
                        house_in_db.property_use = property_type
                        house_in_db.last_update_date = datetime.date.today()
                        house_in_db.save()
                    latest_sale = RealEstateSales.objects \
                        .filter(real_estate_properties_id=house_in_db.id) \
                        .order_by('-sale_date')
                    print("got sale")
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
                n[0].last_updated = datetime.datetime.now(datetime.timezone.utc)
                n[0].save()
                #SUCCESS
                return 'Update queued for neighborhood: ' + str(id)
        except:
            print("continue")


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

    filter_link_element = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.ID, "filter_SaleDate"))
    )

    # Click on the link
    filter_link_element.click()

    print("found sale date filter")

    # TODAY button
    # Wait for the parent div with id "SaleDateEndC" to be visible
    parent_div = WebDriverWait(browser, 10).until(
        EC.visibility_of_element_located((By.ID, "SaleDateEndC"))
    )

    # Find the <td> element under the parent div
    td_element = parent_div.find_element(By.XPATH, ".//td[contains(@class, 'dp_today')]")

    # Click on the <td> element
    td_element.click()

    # click the filter element again to get it to go away
    filter_link_element = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.ID, "filter_SaleDate"))
    )

    # Click on the link
    filter_link_element.click()

    print("found td element")
    # ORDER dropdown to get order by date
    # Wait for the dropdown menu to be clickable
    # Wait for the first link ("sortButton") to be clickable
    first_link = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.ID, "sortButton"))
    )

    # Click on the first link
    first_link.click()

    print("found sort dropdown element")

    # Wait for the second link ("sortDate") to be clickable
    second_link = WebDriverWait(browser, 10).until(
        EC.element_to_be_clickable((By.ID, "sortDate"))
    )

    # Click on the second link
    second_link.click()

    print("found sort date element")

    # Get the updated HTML content after clicking
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "body"))
    )

    # Get the page source
    page_source = browser.page_source

    # elem = myProperty.click()
    # browser.execute_script("arguments[0].click();", myProperty)

    return page_source

def get_address_id(location, n_latitude, n_longitude):
    # sql = """select id
    #             from tn_davidson_addresses t
    #             where %s like concat('%',add_number,'%')
    #             and %s like concat('%',streetname,'%')
    #             order by abs(%s-latitude)
    #             limit 1
    #             ;
    #             """
    # user_input = (location, location, neighborhood_latitude)
    # cursor = cnx.cursor()
    # cursor.execute(sql, user_input)
    # rows = cursor.fetchall()
    # cursor.close()
    # if len(rows) > 0:
    #     return rows[0][0]
    # else:
    #     return 'NULL'
    # Maybe do this later
    return None