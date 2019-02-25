from selenium import webdriver
import ast
import time
import csv
from googletrans import Translator

this_url = "https://goo.gl/VrRbiP"
short_delay = 0.5
long_delay = 5
csv_path = "C://Users/arman/Desktop/crawlers/ApplyAbroad-Crawler/applyabroad_reject.csv"
csv_header = ["BSc University", "BSc Major", "BSc GPA", "MSc University", "MSc Major", "MSc GPA", "TOEFL/IELTS",
              "GRE.Quant", "GRE.Verbal", "GRE.Writing", "Total Papers", "ISI", "International", "Local",
              "Academic Experience", "Work Experience", "Accept?", "Major", "Fund?", "Fund Amount",
              "Target University", "Field", "Country", "Year"]


def init_csv_reader(path):
    csv_file = open(path, mode='a', newline='')
    writer = csv.writer(csv_file, delimiter=',', quotechar='"')
    writer.writerow(csv_header)
    return writer, csv_file


def append_to_csv(record, csv_file, writer):
    writer.writerow(record)
    csv_file.flush()


def init_driver(address):
    driver = webdriver.Chrome()
    driver.get(url=address)
    return driver


def go_to_next_page(driver):
    time.sleep(short_delay)
    next_button = driver.find_elements_by_xpath("//span[@class='prev_next']/a[@rel='next']")[0]
    next_button.click()
    time.sleep(long_delay)


def is_english(complex_text):
    try:
        complex_text.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True


# deprecated! we ought to use google-translate REST-API
# def translate_to_english(complex_text):
#     translator_driver = webdriver.Chrome()
#     translator_driver.get("https://translate.google.com/")
#     text_input = translator_driver.find_element_by_xpath("//textarea[@id='source']")
#     text_input.send_keys(complex_text)
#     time.sleep(short_delay * 3)
#     result_text = translator_driver.find_element_by_id("result_box")
#     time.sleep(short_delay)
#     translator_driver.close()
#     return result_text


def translate_to_english(complex_text):
    translator = Translator()
    translated = translator.translate(text=complex_text, dest='fa', src='en')
    try:
        iter(translated)
        translated_text = list()
        for translated_word in translated:
            translated_text.append(translated_word.text)
    except TypeError:
        translated_text = translated.text
    return translated_text


driver = init_driver(address=this_url)
writer, csv_file = init_csv_reader(path=csv_path)
last_page_reached = False

while last_page_reached is False:

    posts = driver.find_elements_by_xpath("//blockquote[@class='postcontent restore ']")
    posts = posts[2:]
    for post in posts:

        this_post = post.text
        lines = this_post.split("\n")

        bsc_univ = None
        bsc_major = None
        bsc_avg = None

        msc_univ = None
        msc_major = None
        msc_avg = None

        toefl_or_ielts = None
        gre_quant = None
        gre_verbal = None
        gre_writing = None

        total_papers = None
        isi = None
        international_papers = None
        local_papers = None

        academic_experience = None
        work_experience = None

        result = "no"
        major = None
        got_fund = "-"
        fund_amount = "-"
        target_univ = None
        field = None
        country = None
        year = "2014"

        for line in lines:

            if line.find("نام رشته تحصیلی و مقطع آن") != -1:

                if line.find("PhD") != -1 or line.find("Doctorate") != -1 or line.find("دکتر"):
                    major = "PhD"
                else:
                    major = "-"

                content = str(line.split(":")[1:])
                content = content.strip().split()
                try:
                    content.pop(content.index("PhD"))
                except:
                    pass
                try:
                    content.pop(content.index("PhD-"))
                except:
                    pass
                try:
                    content.pop(content.index("-"))
                except:
                    pass
                try:
                    content.pop(content.index("in"))
                except:
                    pass

                field = ' '.join(content)
                # print(field)

            if line.find("نام دانشگاه مقصد") != -1:
                target_univ = line.split(":")[1:]
                # print(target_univ)

            if line.find("نام دانشگاه کارشناسی") != -1:
                content = line.split(":")[1:]
                content = ' '.join(content)
                if content.find("کارشناسی ارشد") != -1:
                    bsc_msc = content
                else:
                    bsc = content

            if line.find("معدل کارشناسی") != -1:
                content = line.split()
                gpa_field = list()
                for word in content:
                    if word.isdigit() or not word.isalnum():
                        gpa_field.append(word)

            if line.find("GRE") != -1:
                quant_or_verbal = list()
                content = line.split()
                for word in content:
                    if word.isdigit() or not word.isalnum():
                        try:
                            this_score = ast.literal_eval(word)
                            if this_score < 5:
                                gre_writing = this_score
                            else:
                                quant_or_verbal.append(this_score)
                        except:
                            pass
                try:
                    gre_verbal = min(quant_or_verbal)
                    gre_quant = max(quant_or_verbal)
                except:
                    pass

            if line.find("تافل") != -1 or line.find("آیلتس") != -1:
                content = line.split()
                for word in content:
                    if word.isdigit():
                        toefl_or_ielts = word

            if line.find("نعداد و نوع مقالات") != -1:
                content = line.split(":")
                total_papers = content[1:]

            if line.find("سابقه کار") != -1:
                content = line.split(":")
                work_experience = content[1:]

        try:
            bsc_univ = bsc_msc
        except:
            try:
                bsc_univ = bsc
                msc_major = "-"
                msc_field = "-"
                msc_avg = "-"
            except:
                pass
        try:
            bsc_avg = gpa_field
        except:
            pass

        this_record = [bsc_univ, bsc_major, bsc_avg, msc_univ, msc_major, msc_avg, toefl_or_ielts, gre_quant, gre_verbal,
                       gre_writing, total_papers, isi, international_papers, local_papers, academic_experience,
                       work_experience, result, major, got_fund, fund_amount, target_univ, field, country, year]

        # print(this_record)
        for array in range(len(this_record)):
            try:
                if not is_english(this_record[array]):
                    this_record[array] = translate_to_english(this_record[array])
            except:
                pass

        print(this_record)
        append_to_csv(record=this_record, csv_file=csv_file, writer=writer)

    try:
        go_to_next_page(driver=driver)
    except:
        print("Uh! We've reached the last page!")
        last_page_reached = True

driver.close()


