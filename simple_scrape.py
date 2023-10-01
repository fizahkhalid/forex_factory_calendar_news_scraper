try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    driver = webdriver.Chrome()

except:
    print ("AF: No Chrome webdriver installed")
    driver = webdriver.Chrome(ChromeDriverManager().install())
    
import json
import time
import pandas as pd
from datetime import datetime
from webdriver_manager.chrome import ChromeDriverManager

from config import ALLOWED_ELEMENT_TYPES,ICON_COLOR_MAP

driver.get("https://www.forexfactory.com/calendar?month=this")

month = datetime.now().strftime("%B")

table = driver.find_element(By.CLASS_NAME, "calendar__table")

data = []
for row in table.find_elements(By.TAG_NAME,"tr"):
    row_data = []
    for element in row.find_elements(By.TAG_NAME,"td"):
        class_name = element.get_attribute('class')
        if class_name in ALLOWED_ELEMENT_TYPES:
            if element.text:
                row_data.append(element.text)
            elif "calendar__impact" in class_name:
                impact_elements = element.find_elements(By.TAG_NAME,"span")
                for impact in impact_elements:
                    impact_class = impact.get_attribute("class")
                    color =ICON_COLOR_MAP[impact_class]
                if color:
                    row_data.append(color)
                else:
                    row_data.append("impact")

    if len(row_data):
        data.append(row_data)