import serial
import urllib.request, urllib.parse, urllib, xml.dom.minidom, urllib.error, datetime
import json, time
from pygeocoder import Geocoder

def get_weather():
    #wunderground weather of place specified in 'zipcode'
    zipcode = '95050'

    url = "http://api.wunderground.com/auto/wui/geo/WXCurrentObXML/index.xml?query=" + urllib.parse.quote(zipcode)
    dom = xml.dom.minidom.parse(urllib.request.urlopen(url))
    city = dom.getElementsByTagName('display_location')[0].getElementsByTagName('full')[0].childNodes[0].data
    if city != ", ":
        temp_f = dom.getElementsByTagName('temp_f')[0].childNodes[0].data
        temp_c = dom.getElementsByTagName('temp_c')[0].childNodes[0].data
        try:
            condition = dom.getElementsByTagName('weather')[0].childNodes[0].data
        except:
            condition = ""
        try:
            humidity = str(dom.getElementsByTagName('relative_humidity')[0].childNodes[0].data)
        except:
            humidity = ""
        try:
            wind = "Wind: " + str(dom.getElementsByTagName('wind_string')[0].childNodes[0].data)
        except:
            wind = ""

        degree_symbol = chr(176)
        #output = "%s / %s / %s%sF %s%sC / %s / %s" % (city,
        #                                               condition,
        #                                               temp_f,
        #                                               degree_symbol,
        #                                               temp_c,
        #                                               degree_symbol,
        #                                               humidity,
        #                                               wind)
        output = "%s\r%sF %sC Hum: %s" % (city,temp_f, temp_c, humidity)

        return output.encode()
def get_quake_data():
    #Altername URLS for intensities: http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
    request = urllib.request.urlopen("http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
    quake = json.loads(request.read().decode())
    request.close()
    quake = quake['features'][0] #select the latest quake
    qtitle = quake['properties']['title']
    mag = quake['properties']['mag']
    updated = round(quake['properties']['time'] / 1000)
    updated = datetime.datetime.fromtimestamp(updated)
    ago = round((datetime.datetime.now() - updated).seconds / 60)
    lat = quake['geometry']['coordinates'][0]
    lon = quake['geometry']['coordinates'][1]



    quakestring = "Earthquake: M%s%s %s min" % (mag, rev_geocode(lat,lon), ago)
    quakestring = quakestring.ljust(32)

    return quakestring.encode()

def rev_geocode(lat,lon):
    results = Geocoder.reverse_geocode(19.4,-155.2798)

    country = results.raw[5]['address_components'][0]['short_name']
    state = results.raw[4]['address_components'][0]['short_name']
    city = results.raw[2]['address_components'][0]['short_name']

    return "%s, %s" % (city,state)

    
#LCD Command definitions
CLS = b'\xFE\x58'

BACKLIGHT_ON=b'\xFE\x42'
BACKLIGHT_OFF=b'\xFE\x46'

CONTRAST = b'\xFE\x50'

BACKLIGHT_BRIGHTNESS = b'\xFE\x99'
BACKLIGHT_ORANGE= b'\xFE\xD0\xFF\x01\x00'
BACKLIGHT_TEAL= b'\xFE\xD0\x00\xFF\xFF'

AUTOSCROLL_ON = b'\xFE\x51'
AUTOSCROLL_OFF = b'\xFE\x52'
#END LCD Command Definitions
ser = serial.Serial(port='COM4', baudrate=9600)  # open first serial port

def init_lcd(ser):
    
    ser.write(CONTRAST + bytes([185])) #185 seems to be a good value for contrast
    ser.write(BACKLIGHT_BRIGHTNESS + b'\xFF')        
    ser.write(BACKLIGHT_TEAL)      # write a string
    ser.write(AUTOSCROLL_OFF)
    ser.write(CLS) #clear display

init_lcd(ser)
while(1):
    ser.write(get_weather())
    time.sleep(2)
    ser.write(get_quake_data())
    time.sleep(2)

