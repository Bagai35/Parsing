import mysql.connector
from xml.etree import ElementTree
import requests

create_database_query = "CREATE DATABASE IF NOT EXISTS country_info"

mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password=""
)

mycursor = mydb.cursor()
mycursor.execute(create_database_query)
mycursor.execute("USE country_info")

create_user_query = "CREATE USER IF NOT EXISTS 'country_info'@'localhost' IDENTIFIED BY 'country'"
grant_privileges_query = "GRANT ALL PRIVILEGES ON country_info.* TO 'country_info'@'localhost'"
flush_privileges_query = "FLUSH PRIVILEGES"

mycursor.execute(create_user_query)
mycursor.execute(grant_privileges_query)
mycursor.execute(flush_privileges_query)

mycursor.execute('''
CREATE TABLE IF NOT EXISTS country_info (
    name VARCHAR(255),
    code VARCHAR(5),
    currency VARCHAR(255),
    capital VARCHAR(255),
    phone VARCHAR(255),
    continent VARCHAR(255),
    flag VARCHAR(255),
    languages VARCHAR(255)
)
''')

mydb.commit()

mycursor.close()
mydb.close()

# Повторное открытие соединения после закрытия
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="country_info"
)

url = "http://webservices.oorsprong.org/websamples.countryinfo/CountryInfoService.wso"

payload = """<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Body>
    <FullCountryInfoAllCountries xmlns="http://www.oorsprong.org/websamples.countryinfo">
    </FullCountryInfoAllCountries>
  </soap:Body>
</soap:Envelope>"""

headers = {
    'Content-Type': 'text/xml; charset=utf-8'
}

response = requests.request("POST", url, headers=headers, data=payload)
response_xml = response.text.replace('soap:', '').replace('m:', '')
xml_text = ElementTree.fromstring(response_xml)

insert_query = """
INSERT INTO country_info (name, code, currency, capital, phone, continent, flag, languages)
VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
"""

data = []
for country in xml_text.findall('.//tCountryInfo'):
    name = country.find('sName').text
    code = country.find('sISOCode').text
    currency = country.find('sCurrencyISOCode').text
    capital = country.find('sCapitalCity').text
    phone = country.find('sPhoneCode').text
    continent = country.find('sContinentCode').text
    flag = country.find('sCountryFlag').text

    languages = []
    for language in country.findall('.//Languages/tLanguage'):
        language_name = language.find('sName').text
        languages.append(language_name)

    data.append((name, code, currency, capital, phone, continent, flag, ','.join(languages)))

mycursor = mydb.cursor()
mycursor.executemany(insert_query, data)
mydb.commit()

mycursor.close()
mydb.close()
