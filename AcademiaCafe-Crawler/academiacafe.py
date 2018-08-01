from selenium import webdriver
import time
import csv
# import pandas as pd
# import numpy as np
# import ast


csv_path = "C://Users/arman/Desktop/Academia-Cafe-Data.csv"
csv_file = open(csv_path, mode='a', newline='')

# csv_file = pd.read_csv(csv_path)
# column_keys = list(csv_file.columns)
# print(column_keys)

driver = webdriver.Chrome()
url = "https://www.academiacafe.com/admission/index.php?r=univsApplied/index"
driver.get(url=url)
loop_interrupt = False

while loop_interrupt is False:

    # check whether the page is loaded completely or wait a little and try again!
    loaded_page = False
    logo_tag = driver.find_element_by_id("logo")
    while loaded_page is False:
        if logo_tag.size:
            loaded_page = True
        else:
            print("current page is not loaded yet! check the net connectivity")
            time.sleep(5)

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
        # print(row_data[11])

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
        detail_button = row.find_element_by_css_selector("i.fa.fa-search")
        detail_button.click()
        time.sleep(1)

        # check whether the modal box is loaded or wait a moment and try again!
        modal_box_loaded = False
        modal_title_tag = driver.find_element_by_id("details_view")
        while modal_box_loaded is False:
            modal_box_height = modal_title_tag.size['height']
            if modal_box_height > 20:
                modal_box_loaded = True
            else:
                print("modal box not opened yet! check the net connectivity!")
                time.sleep(5)

        modal_box = driver.find_element_by_id("dlg-univs-applied-view")
        box_text = modal_box.text
        box_text = box_text.split("\n")
        # print(box_text)

        bsc_major = '-'
        bsc_univ = '-'
        bsc_avg = '-'
        msc_major = '-'
        msc_univ = '-'
        msc_avg = '-'
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

            if element.find("GRE General") != -1:
                this_element = box_text[box_text.index(element) + 1]
                this_element = this_element.split()[-1].split(",")
                gre_quant = this_element[0]
                gre_verbal = this_element[1]
                gre_writing = this_element[2]

            if element.find("Papers: ") != -1:
                if element.find("International Journal Papers: ") != -1:
                    num_intl_journals = int(element.split()[-1])
                elif element.find("International Conference/Workshop Papers: ") != -1:
                    num_intl_confs = int(element.split()[-1])
                elif element.find("Local Conference/Workshop Papers: ") != -1:
                    num_local_confs = int(element.split()[-1])
                elif element.find("Local Journal Papers: ") != -1:
                    num_local_journals = int(element.split()[-1])

            # noinspection PyBroadException
            try:
                total_papers = num_local_confs + num_local_journals + num_intl_journals + num_intl_confs
                international_papers = num_intl_journals + num_intl_confs
                local_papers = num_local_confs + num_local_journals
            except Exception:
                pass

            if element.find("Work Experience: ") != -1:
                this_element = box_text[box_text.index(element)]
                # print(this_element)
                for word in this_element.split():
                    if word.isdigit():
                        work_experience = word
                        # break

            if element.find("ISI") != -1:
                isi = 1
            else:
                isi = 0

        # try:
        #     print("local:", local_papers)
        #     print("intl:", international_papers)
        #     print("work:", work_experience)
        #     print("total:", total_papers)
        #     print("GRE:", gre_quant, gre_verbal, gre_writing)
        # except:
        #     pass

        btn = "button.ui-button.ui-widget.ui-state-default.ui-corner-all.ui-button-icon-only.ui-dialog-titlebar-close"
        close_button = driver.find_element_by_css_selector(btn)
        close_button.click()
        time.sleep(0.5)

        this_record = [bsc_univ, bsc_major, bsc_avg, msc_univ, msc_major, msc_avg, toefl_or_ielts, gre_quant, gre_verbal,
                       gre_writing, total_papers, isi, international_papers, local_papers, academic_experience,
                       work_experience, result, major, got_fund, fund_amount, target_univ, field, country, year]

        writer = csv.writer(csv_file, delimiter=',', quotechar='"')
        writer.writerow(this_record)
        csv_file.flush()

        # this_record = pd.DataFrame(this_record)
        # this_record.to_csv(csv_path, mode='a', index=False, columns=None)
        # print(this_record)
        # csv_file.append(this_record)
        # print(csv_file)

    # noinspection PyBroadException
    if driver.find_elements_by_css_selector("li.next.hidden"):
        print("uh! we've reached the end :))")
        loop_interrupt = True
    else:
        next_btn = driver.find_element_by_class_name("next")
        next_btn.click()
        time.sleep(1)

driver.close()
csv_file.close()
