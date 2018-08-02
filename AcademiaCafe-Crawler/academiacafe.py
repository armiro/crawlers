from selenium import webdriver
import time
import csv
# import pandas as pd
# import numpy as np
# import ast

csv_path = "C://Users/arman/Desktop/data.csv"
this_url = "https://www.academiacafe.com/admission/index.php?r=univsApplied/index"
long_delay = 5
short_delay = 0.5


def initialize_csv_reader(path):
    csv_file = open(path, mode='a', newline='')
    writer = csv.writer(csv_file, delimiter=',', quotechar='"')
    return writer, csv_file


def append_to_csv(record, csv_file, writer):
    writer.writerow(record)
    csv_file.flush()


def initialize_webdriver(url):
    driver = webdriver.Chrome()
    driver.get(url=url)
    return driver


def check_page_loading(driver):
    loaded_page = False
    logo_tag = driver.find_element_by_id("logo")
    while loaded_page is False:
        if logo_tag.size:
            loaded_page = True
        else:
            print("current page is not loaded yet! check the net connectivity")
            time.sleep(long_delay)


def find_bsc_data(element, box_text, bsc_avg):
    if element.find("Bachelors ") != -1:
        split_element = element.split()
        bsc_major = ' '.join(split_element[2:])
        bsc_univ = box_text[box_text.index(element) + 1]
        gpa_field = box_text[box_text.index(element) + 2]
        gpa_field = gpa_field.split()
        if bsc_avg == "-":
            bsc_avg = gpa_field[2]
        else:
            pass
        return bsc_major, bsc_univ, bsc_avg


def find_msc_data(element, box_text, msc_avg):
    if element.find("Masters ") != -1:
        split_element = element.split()
        msc_major = ' '.join(split_element[2:])
        msc_univ = box_text[box_text.index(element) + 1]
        gpa_field = box_text[box_text.index(element) + 2]
        gpa_field = gpa_field.split()
        if msc_avg == "-":
            msc_avg = gpa_field[2]
        else:
            pass
        return msc_major, msc_univ, msc_avg


def find_GRE_score(element, box_text):
    if element.find("GRE General") != -1:
        this_element = box_text[box_text.index(element) + 1]
        this_element = this_element.split()[-1].split(",")
        gre_quant = this_element[0]
        gre_verbal = this_element[1]
        gre_writing = this_element[2]
        return gre_quant, gre_verbal, gre_writing


def find_work_experience(element, box_text):
    if element.find("Work Experience: ") != -1 or element.find("سابقه کار:") != -1:
        this_element = box_text[box_text.index(element)]
        # print(this_element)
        for word in this_element.split():
            if word.isdigit():
                work_experience = word
                return work_experience
                # break


def find_isi(element):
    if element.find("ISI") != -1 or element.find("isi") != -1:
        isi = 1
    else:
        isi = 0
    return isi


def check_modal_box_loading(driver):
    modal_box_loaded = False
    modal_title_tag = driver.find_element_by_id("details_view")
    while modal_box_loaded is False:
        modal_box_height = modal_title_tag.size['height']
        if modal_box_height > 20:
            modal_box_loaded = True
        else:
            print("modal box not opened yet! check the net connectivity!")
            time.sleep(long_delay)


def click_detail_button(row):
    detail_button = row.find_element_by_css_selector("i.fa.fa-search")
    detail_button.click()
    time.sleep(short_delay)


def close_modal_box(driver):
    btn = "button.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-icon-only.ui-dialog-titlebar-close"
    close_button = driver.find_element_by_css_selector(btn)
    close_button.click()
    time.sleep(short_delay)


def click_next_button(driver):
    next_btn = driver.find_element_by_class_name("next")
    next_btn.click()
    time.sleep(short_delay)


def close_all(driver, csv_file):
    driver.close()
    csv_file.close()


def main():

    writer, csv_file = initialize_csv_reader(path=csv_path)
    driver = initialize_webdriver(url=this_url)

    loop_interrupt = False
    while loop_interrupt is False:

        # check whether the page is loaded completely or wait a little and try again!
        check_page_loading(driver)

        table = driver.find_element_by_xpath('//*[@class="items"]/tbody')
        rows = table.find_elements_by_xpath(".//tr")

        for row in rows:
            row_text = row.get_attribute("innerHTML")
            # print(row_text)
            univ_last = row_text.find("</a>")
            univ_first = row_text.find(">", univ_last - 50, univ_last)
            target_univ = row_text[univ_first + 1: univ_last]
            # print(target_univ)

            indices = list()
            chars = list()
            for index, char in enumerate(row_text):
                indices.append(index)
                chars.append(char)

            td_indices = list()
            back_td_indices = list()
            for index in indices:
                if ''.join(chars[index: index + 4]) == "<td>" or ''.join(chars[index: index + 4]) == "<td ":
                    td_indices.append(index + 4)
                if ''.join(chars[index: index + 5]) == "</td>":
                    back_td_indices.append(index)

            # print("td indices:", td_indices)
            # print("back_td_indices:", back_td_indices)
            row_data = list()
            for element in range(len(td_indices)):
                row_data.append(row_text[td_indices[element]: back_td_indices[element]])

            # print(row_data)
            field = row_data[1]
            country = row_data[2]
            major = row_data[3]

            bsc_avg = row_data[5]
            msc_avg = row_data[6]

            if row_data[7] == "-":
                if row_data[8] == "-":
                    toefl_or_ielts = row_data[7]
                else:
                    toefl_or_ielts = row_data[8]
            else:
                toefl_or_ielts = row_data[7]

            # gre = row_data[9]
            year = row_data[10]

            fund = int(row_data[4])
            if row_data[11].find("Admitted") != -1:
                result = "yes"
                if fund is 0:
                    got_fund = "no"
                    fund_amount = 0
                else:
                    got_fund = "yes"
                    fund_amount = fund
            else:
                # print('reject found!')
                result = "no"
                got_fund = "-"
                fund_amount = "-"

            # visa = row_data[12]
            click_detail_button(row=row)

            # check whether the modal box is loaded or wait a moment and try again!
            check_modal_box_loading(driver=driver)

            modal_box = driver.find_element_by_id("dlg-univs-applied-view")
            box_text = modal_box.text
            box_text = box_text.split("\n")
            # print(box_text)

            bsc_major = '-'
            bsc_univ = '-'
            # bsc_avg = '-'
            msc_major = '-'
            msc_univ = '-'
            # msc_avg = '-'
            gre_quant = '-'
            gre_verbal = '-'
            gre_writing = '-'
            total_papers = 0
            international_papers = 0
            local_papers = 0
            work_experience = 0
            academic_experience = 0
            isi = 0

            for element in box_text:

                try:
                    bsc_major, bsc_univ, bsc_avg = find_bsc_data(element=element, box_text=box_text, bsc_avg=bsc_avg)
                except:
                    pass
                try:
                    msc_major, msc_univ, msc_avg = find_msc_data(element=element, box_text=box_text, msc_avg=msc_avg)
                except:
                    pass
                try:
                    gre_quant, gre_verbal, gre_writing = find_GRE_score(element=element, box_text=box_text)
                except:
                    pass

                if element.find("Papers: ") != -1 or element.find("تعداد مقالات") != -1:
                    if element.find("International Journal Papers: ") != -1 or element.find(
                            "تعداد مقالات ژورنال بین‌المللی:") != -1:
                        num_intl_journals = int(element.split()[-1])
                    elif element.find("International Conference/Workshop Papers: ") != -1 or element.find(
                            "تعداد مقالات کنفرانس بین‌المللی:") != -1:
                        num_intl_confs = int(element.split()[-1])
                    elif element.find("Local Conference/Workshop Papers: ") != -1 or element.find(
                            "تعداد مقالات کنفرانس داخلی:") != -1:
                        num_local_confs = int(element.split()[-1])
                    elif element.find("Local Journal Papers: ") != -1 or element.find(
                            "تعداد مقالات ژورنال داخلی:") != -1:
                        num_local_journals = int(element.split()[-1])

                # noinspection PyBroadException
                try:
                    total_papers = num_local_confs + num_local_journals + num_intl_journals + num_intl_confs
                    international_papers = num_intl_journals + num_intl_confs
                    local_papers = num_local_confs + num_local_journals
                except Exception:
                    pass

                work_experience = find_work_experience(element=element, box_text=box_text)

                isi = find_isi(element=element)

            close_modal_box(driver=driver)

            this_record = [bsc_univ, bsc_major, bsc_avg, msc_univ, msc_major, msc_avg, toefl_or_ielts, gre_quant,
                           gre_verbal,
                           gre_writing, total_papers, isi, international_papers, local_papers, academic_experience,
                           work_experience, result, major, got_fund, fund_amount, target_univ, field, country, year]

            append_to_csv(record=this_record, csv_file=csv_file, writer=writer)

        # noinspection PyBroadException
        if driver.find_elements_by_css_selector("li.next.hidden"):
            print("uh! we've reached the end :))")
            loop_interrupt = True
        else:
            click_next_button(driver=driver)

    close_all(driver=driver, csv_file=csv_file)


if __name__ == '__main__':

    main()
