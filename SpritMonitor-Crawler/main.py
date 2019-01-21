from selenium import webdriver
import time

url = 'https://www.spritmonitor.de/en/search.html'
driver = webdriver.Chrome(keep_alive=True)
driver.get(url=url)

time.sleep(1.)

vehicle_type_box = driver.find_element_by_name(name='vehicletype')
vehicle_type_box.click()
electricity = vehicle_type_box.find_element_by_xpath(xpath="option[@value='1']")
electricity.click()

time.sleep(1.)

fuel_type_box = driver.find_element_by_name(name='fueltype')
fuel_type_box.click()
electricity = fuel_type_box.find_element_by_xpath(xpath="option[@value='5']")
electricity.click()

time.sleep(1.)

# min_km_box = driver.find_element_by_id(id_='minkm')
# min_km_box.clear()
# min_km_box.send_keys('50')

time.sleep(2.)

driver.find_element_by_id(id_='add').click()

time.sleep(2.)

result_table = driver.find_element_by_css_selector(css_selector="table.searchresults")
# print(result_table.get_attribute(name='innerHTML'))
rows = result_table.find_elements_by_xpath(".//tr")
print("num of rows is:", len(rows))
print(rows[1].get_attribute(name='innerHTML'))
# for row in rows:
#     print(row.get_attribute(name='innerHTML'))
#     try:
#         fueling_quantity = row.find_element_by_xpath(xpath="//img")
#         fueling_quantity = fueling_quantity.get_attribute(name='src')
#         print(fueling_quantity)
#         description = row.find_element_by_class_name(name='description')
#         vehicle_link = description.find_element_by_xpath(xpath="//a")
#         vehicle_link.click()
#     except:
#         pass

