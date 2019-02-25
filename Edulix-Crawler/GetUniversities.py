from selenium import webdriver
import time

driver = webdriver.Chrome()
driver.get("https://www.topuniversities.com/university-rankings/world-university-rankings/2019")
time.sleep(5)
# driver.refresh()

last_page_reached = False
universities = list()

while last_page_reached is False:
    table = driver.find_element_by_xpath("//*[@id='qs-rankings']/tbody")
    univ_names = table.find_elements_by_xpath(".//a[@class='title']")
    for univ_name in univ_names:
        name = univ_name.text
        split = name.split()
        if split[-1].find("(") != -1 and split[-1].find(")") != -1:
            split.pop()
            name = ' '.join(split)
        if name.find(",") != -1:
            name.replace(",", "")
        universities.append(name)
    try:
        next_page = driver.find_element_by_xpath("//a[@class='paginate_button next']")
        next_page.click()
        time.sleep(1)
    except:
        print("University names collected successfully!")
        last_page_reached = True

driver.close()
