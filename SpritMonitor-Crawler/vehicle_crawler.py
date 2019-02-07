from selenium import webdriver
import time
import csv


csv_header = ['manufacturer', 'model', 'version', 'power(kW)', 'fuel_date', 'odometer', 'trip_distance(km)',
              'quantity(kWh)', 'fuel_type', 'tire_type', 'city', 'motor_way', 'country_roads', 'driving_style',
              'consumption(kWh/100km)', 'A/C', 'park_heating', 'avg_speed(km/h)', 'fuel_note']
csv_path = "C://Users/arman/Desktop/crawlers/SpritMonitor-Crawler/data.csv"


def initialize_csv_reader(path):
    csv_file = open(path, mode='a', newline='')
    writer = csv.writer(csv_file, delimiter=',', quotechar='"')
    writer.writerow(csv_header)
    return writer, csv_file


def append_to_csv(record, csv_file, writer):
    writer.writerow(record)
    csv_file.flush()


writer, csv_file = initialize_csv_reader(path=csv_path)
url = 'https://www.spritmonitor.de/en/detail/804546.html'
driver = webdriver.Chrome(keep_alive=True)
driver.get(url=url)

time.sleep(2.)

details = driver.find_element_by_id(id_="vehicledetails")
vehicle = str(details.find_element_by_xpath(xpath="//h1").text)
vehicle = vehicle.split(sep="-")

manufacturer = vehicle[0].strip()
model = vehicle[1].strip()
version = vehicle[2].strip()

engine_power = None
try:
    vehicle_detail = str(details.find_element_by_xpath(xpath="//font").text).split()
    for word in range(0, len(vehicle_detail) - 1):
        if vehicle_detail[word] == "kW":
            engine_power = vehicle_detail[word - 1]
except:
    pass


table = driver.find_element_by_xpath(xpath="//table[@class='itemtable']/tbody")
rows = table.find_elements_by_xpath(xpath=".//tr")
# print(rows[0].get_attribute(name="innerHTML"))

for row in rows:
    features = row.find_elements_by_xpath(xpath=".//td")

    if features[0].get_attribute(name="class") == "fueldate":
        fuel_date = features[0].text
    else:
        fuel_date = None
    print("fuel_date is:", fuel_date)

    # check whether this is a fueling record, or go to the next record directly
    if fuel_date is None:
        continue

    if features[1].get_attribute(name="class") == "fuelkmpos":
        odometer = features[1].text
    else:
        odometer = None
    print("odometer is:", odometer)

    if features[2].get_attribute(name="class") == "trip":
        distance = features[2].text
    else:
        distance = None
    print("trip distance is:", distance)

    if features[3].get_attribute(name="class") == "quantity":
        quantity = features[3].text
    else:
        quantity = None
    print("quantity is:", quantity)

    if features[4].get_attribute(name="class") == "fuelsort":
        fuel_type = features[4].get_attribute(name="onmouseover").split(sep="'")[1]
    else:
        fuel_type = None
    print("fuel type is:", fuel_type)

    if features[5].get_attribute(name="class") == "tire":
        try:
            tire_img = features[5].find_element_by_xpath(xpath=".//img")
            tire_type = tire_img.get_attribute(name="onmouseover").split(sep="'")[1]
        except:
            tire_type = None
    else:
        tire_type = None
    print("tire type is:", tire_type)

    if features[6].get_attribute(name="class") == "street":
        try:
            street_imgs = features[6].find_elements_by_xpath(xpath=".//img")
            city = country_roads = motor_way = 0
            for street_img in street_imgs:
                if street_img.get_attribute(name="onmouseover").split(sep="'")[1] == 'City':
                    city = 1
                if street_img.get_attribute(name="onmouseover").split(sep="'")[1] == 'Motor-way':
                    motor_way = 1
                if street_img.get_attribute(name="onmouseover").split(sep="'")[1] == 'Country roads':
                    country_roads = 1
        except:
            city = country_roads = motor_way = None
    else:
        city = country_roads = motor_way = None
    print("streets are:", motor_way, city, country_roads)

    if features[7].get_attribute(name="class") == "style":
        try:
            style_img = features[7].find_element_by_xpath(xpath=".//img")
            style = style_img.get_attribute(name="onmouseover").split(sep="'")[1]
        except:
            style = None
    else:
        style = None
    print("driving style is:", style)

    if features[9].get_attribute(name="class") == "consumption":
        try:
            consumption = features[9].get_attribute(name="onmouseover").split("'")[1].split(" ")[0]
        except:
            consumption = None
    else:
        consumption = None
    print("consumption is:", consumption)

    avg_speed = None
    AC = park_heating = 0
    if features[10].get_attribute(name="class") == "fuelnote":
        try:
            fuel_note_imgs = features[10].find_elements_by_xpath(xpath=".//img")
            fuel_notes = list()
            for fuel_note_img in fuel_note_imgs:
                if fuel_note_img.get_attribute(name='alt') == 'Bordcomputer':
                    bordcomputer = fuel_note_img.get_attribute(name="onmouseover").split("'")[1]
                    words = bordcomputer.split()
                    for word in words:
                        if word.find("Consumption") != -1:
                            idx = words.index(word)
                            consumption = words[idx + 1]
                        elif word.find("Quantity") != -1:
                            idx = words.index(word)
                            quantity = words[idx + 1]
                        elif word.find("Avg speed") != -1:
                            idx = words.index(word)
                            avg_speed = words[idx + 1]
                        else:
                            pass
                elif fuel_note_img.get_attribute(name='alt') == 'A/C':
                    AC = 1
                elif fuel_note_img.get_attribute(name='alt') == 'Park heating':
                    park_heating = 1
                else:
                    fuel_notes.append(fuel_note_img.get_attribute(name="onmouseover").split("'")[1])
        except:
            fuel_notes = None
    else:
        fuel_notes = None
    print("fuel note is:", fuel_notes)

    this_record = [manufacturer, model, version, engine_power, fuel_date, odometer, distance, quantity,
                   fuel_type, tire_type, city, motor_way, country_roads, style, consumption, AC, park_heating,
                   avg_speed, fuel_notes]

    append_to_csv(record=this_record, csv_file=csv_file, writer=writer)

