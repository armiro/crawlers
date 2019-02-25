# from GetUniversities import universities
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By
import time
import csv

this_url = "http://edulix.com/student-profiles"
csv_header = ["BSc University", "BSc Major", "BSc GPA", "MSc University", "MSc Major", "MSc GPA", "TOEFL/IELTS",
              "GRE.Quant", "GRE.Verbal", "GRE.Writing", "Total Papers", "ISI", "International", "Local",
              "Academic Experience", "Work Experience", "Accept?", "Major", "Fund?", "Fund Amount",
              "Target University", "Field", "Country", "Year"]
usr = 'arman.port@gmail.com'
pwd = 1234567890
long_delay = 10
short_delay = 2
very_short_delay = 0.5
universities = ["Stanford", "Harvard"]


def initialize_csv_writer(header):
    csv_path = "C://Users/arman/Desktop/crawlers/Edulix-Crawler/data.csv"
    csv_file = open(csv_path, mode='a', newline='')
    writer = csv.writer(csv_file, delimiter=',', quotechar='"')
    writer.writerow(header)
    return writer, csv_file


def append_to_csv(is_appendable, writer, file, record):

    if is_appendable is True:
        writer.writerow(record)
        file.flush()
        print("Appended this record...")
    else:
        print('This record is not appendable!')
        is_appendable = True

    return is_appendable


def initialize_driver(url):
    driver = webdriver.Chrome()
    driver.get(url=url)
    return driver


def is_element_present(driver, by_element, element_name):
    element_present = ec.presence_of_element_located((by_element, element_name))
    WebDriverWait(driver=driver, timeout=long_delay).until(element_present)


def login_into_website(driver, username, password):
    login_usr = driver.find_elements_by_css_selector("input.form-control")[0]
    login_pwd = driver.find_elements_by_css_selector("input.form-control")[1]
    login_usr.send_keys(username)
    login_pwd.send_keys(password)
    login_btn = driver.find_element_by_css_selector("button.btn.btn-primary")
    login_btn.click()
    is_element_present(driver=driver, by_element=By.CLASS_NAME, element_name='container-fluid')


def is_univ_name_correct(driver, search_box, tree_item):

    while tree_item.text == "No results found":
        print("univ not found!")
        print("Mistaken? Please input your desired university name:")
        manual_name = str(input())
        search_box.clear()
        search_box.send_keys(manual_name)
        time.sleep(very_short_delay)
        tree_items = driver.find_elements_by_xpath("//li[@role='treeitem']")
        tree_item = tree_items[0]

    return tree_item


def search_student_profiles(driver, univ_name):
    try:
        before_search = driver.find_element_by_class_name("select2-selection__choice__remove")
        before_search.click()
        time.sleep(very_short_delay)
    except:
        pass
    search_box = driver.find_element_by_class_name("select2-search__field")
    search_box.send_keys(univ_name)
    time.sleep(short_delay)
    is_element_present(driver=driver, by_element=By.XPATH, element_name="//li[@role='treeitem']")

    tree_items = driver.find_elements_by_xpath("//li[@role='treeitem']")
    tree_item = tree_items[0]
    tree_item = is_univ_name_correct(driver=driver, tree_item=tree_item, search_box=search_box)

    tree_item.click()

    year_select = driver.find_element_by_id("fromYear")
    from_first = year_select.find_element_by_xpath("./option[@value='2006']")
    from_first.click()
    time.sleep(short_delay)

    search_button = driver.find_element_by_xpath("//*/button[@id='searchStudentProfiles']")
    search_button.click()
    time.sleep(long_delay)

    page_number = driver.find_element_by_class_name("ui-pg-input")
    page_number.clear()
    if page_number.text != "1":
        page_number.send_keys("1")
    else:
        pass
    page_number.clear()
    time.sleep(very_short_delay)


def view_profile(driver, record, main_window, writer, file):
    view = record.find_element_by_xpath("./td[@title='View Profile']")
    view.click()
    time.sleep(long_delay)
    user_window = driver.window_handles[1]
    driver.switch_to.window(user_window)
    panels = driver.find_elements_by_css_selector("div.panel.panel-primary")

    # temporary variables:
    gre_quant = "-"
    gre_verbal = "-"
    gre_writing = "-"
    # finished defining temp. variables

    for panel in panels:

        panel_header = panel.find_element_by_xpath(".//h3[@class='panel-title']")
        header_text = panel_header.text

        if header_text == "Undergrad Information":
            bsc_univ, bsc_major, bsc_avg = extract_undergrad_info(panel=panel)

        if header_text == "Exams Information":
            gre_quant, gre_verbal, gre_writing, toefl_or_ielts = extract_exams_info(panel=panel)

        if header_text == "Applications Information":
            extract_and_export_results(panel=panel, bsc_univ=bsc_univ, bsc_major=bsc_major, bsc_avg=bsc_avg,
                                       toefl_or_ielts=toefl_or_ielts, gre_quant=gre_quant, gre_verbal=gre_verbal,
                                       gre_writing=gre_writing, writer=writer, file=file)

    driver.close()
    driver.switch_to.window(main_window)
    time.sleep(short_delay)


def crawl_profiles(driver, writer, file):

    main_window = driver.window_handles[0]
    last_page_reached = False

    while last_page_reached is False:

        table = driver.find_element_by_xpath("//table[@id='jqGrid']/tbody")
        rows = table.find_elements_by_xpath("./tr[@role='row']")
        rows = rows[1:]
        time.sleep(long_delay)

        for row in rows:
            view_profile(driver=driver, record=row, main_window=main_window, writer=writer, file=file)

        try:
            driver.find_element_by_css_selector("td#next_jqGridPager.ui-pg-button.ui-corner-all.ui-state-disabled")
            print("uh! we have reached the last page!")
            last_page_reached = True
        except:
            go_to_next_page(driver=driver)


def extract_undergrad_info(panel):

    bsc_univ = None
    bsc_major = None
    bsc_avg = None

    forms = panel.find_elements_by_xpath(".//div[@class='form-group']")
    for form in forms:
        text = form.text

        if text.find("College:") != -1:
            bsc_univ = text.split("\n")[-1]
        if text.find("Major:") != -1:
            bsc_major = text.split("\n")[-1]
        if text.find("GPA:") != -1:
            fragment = text.split("\n")[-1]
            bsc_avg = fragment.split("/")[0]

    return bsc_univ, bsc_major, bsc_avg


def extract_exams_info(panel):
    sub_panels = panel.find_elements_by_css_selector("div.well")

    for sub_panel in sub_panels:
        forms = sub_panel.find_elements_by_class_name("form-group")
        sub_panel_header = sub_panel.find_element_by_css_selector("div.alert.alert-info")
        sub_panel_header_text = sub_panel_header.text

        if sub_panel_header_text == "GRE Information":
            for form in forms:
                text = form.text
                if text.find("Quant:") != -1:
                    fragment = text.split("\n")[-1]
                    gre_quant = fragment.split("/")[0]
                    gre_quant = gre_quant.strip()
                    if gre_quant == 0 or not gre_quant.isdigit():
                        gre_quant = "-"

                if text.find("Verbal:") != -1:
                    fragment = text.split("\n")[-1]
                    gre_verbal = fragment.split("/")[0]
                    gre_verbal = gre_verbal.strip()
                    if gre_verbal == 0 or not gre_verbal.isdigit():
                        gre_verbal = "-"

                if text.find("AWA:") != -1:
                    fragment = text.split("\n")[-1]
                    gre_writing = fragment.split("/")[0]
                    gre_writing = gre_writing.strip()
                    if gre_writing == 0 or not gre_writing.isdigit():
                        gre_writing = "-"

        if sub_panel_header_text == "TOEFL Information":
            for form in forms:
                text = form.text
                if text.find("Listening:") != -1:
                    fragment = text.split("\n")[-1]
                    tl = fragment.split("/")[0]
                    tl = tl.strip()
                if text.find("Speaking:") != -1:
                    fragment = text.split("\n")[-1]
                    ts = fragment.split("/")[0]
                    ts = ts.strip()
                if text.find("Reading:") != -1:
                    fragment = text.split("\n")[-1]
                    tr = fragment.split("/")[0]
                    tr = tr.strip()
                if text.find("Writing:") != -1:
                    fragment = text.split("\n")[-1]
                    tw = fragment.split("/")[0]
                    tw = tw.strip()
            toefl = int(tr + tl + ts + tw)
            if toefl == 0:
                toefl_or_ielts = "-"
            else:
                toefl_or_ielts = toefl

        if sub_panel_header_text == "IELTS Information":
            for form in forms:
                text = form.text
                if text.find("Listening:") != -1:
                    fragment = text.split("\n")[-1]
                    ielts_listening = fragment.split("/")[0]
                    ielts_listening = ielts_listening.strip()
                if text.find("Speaking:") != -1:
                    fragment = text.split("\n")[-1]
                    ielts_speaking = fragment.split("/")[0]
                    ielts_speaking = ielts_speaking.strip()
                if text.find("Reading:") != -1:
                    fragment = text.split("\n")[-1]
                    ielts_reading = fragment.split("/")[0]
                    ielts_reading = ielts_reading.strip()
                if text.find("Writing:") != -1:
                    fragment = text.split("\n")[-1]
                    ielts_writing = fragment.split("/")[0]
                    ielts_writing = ielts_writing.strip()
            ielts = int(ielts_reading + ielts_listening + ielts_speaking + ielts_writing) / 4
            if ielts == 0:
                toefl_or_ielts = "-"
            else:
                toefl_or_ielts = ielts

    return gre_quant, gre_verbal, gre_writing, toefl_or_ielts


def extract_and_export_results(panel, bsc_univ, bsc_major, bsc_avg, toefl_or_ielts, gre_quant, gre_verbal, gre_writing, writer, file):

    result = None
    major = None
    target_univ = None
    field = None
    year = None
    appendable = True

    forms = panel.find_elements_by_xpath(".//div[@class='form-group']")
    for form in forms:
        text = form.text
        if text.find("Program:") != -1:
            major = text.split("\n")[-1]
        if text.find("University:") != -1:
            target_univ = text.split("\n")[-1]
        if text.find("Major:") != -1:
            field = text.split("\n")[-1]
        if text.find("Year:") != -1:
            year = text.split("\n")[-1]
        if text.find("Status:") != -1:
            status = text.split("\n")[-1]

            if status == 'Admitted':
                result = 'yes'
            elif status == 'Rejected':
                result = 'no'
            else:
                appendable = False

            this_record = [bsc_univ, bsc_major, bsc_avg, "-", "-", "-", toefl_or_ielts, gre_quant,
                           gre_verbal, gre_writing, 0, 0, 0, 0, 0, 0, result, major, "-", "-",
                           target_univ, field, "US", year]
            appendable = append_to_csv(is_appendable=appendable, writer=writer, file=file, record=this_record)


def go_to_next_page(driver):

    next_page_btn = driver.find_element_by_css_selector("td#next_jqGridPager.ui-pg-button.ui-corner-all")
    next_page_btn.click()
    time.sleep(short_delay)


def main():

    writer, csv_file = initialize_csv_writer(header=csv_header)
    driver = initialize_driver(url=this_url)
    login_into_website(driver=driver, username=usr, password=pwd)

    for university in universities:
        search_student_profiles(driver=driver, univ_name=university)
        crawl_profiles(driver=driver, writer=writer, file=csv_file)


if __name__ == '__main__':

    main()

