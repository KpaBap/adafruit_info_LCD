import serial
import urllib.request, urllib.parse, urllib, xml.dom.minidom, urllib.error, datetime
import json, time, sqlite3, pdb
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

    conn = sqlite3.connect('quakes.sqlite')
    c = conn.cursor()
    result = c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='lastquake';").fetchone()
    if not result:
        c.execute('create table lastquake('
                  'ids text UNIQUE ON CONFLICT REPLACE, '
                  'ts NOT NULL default CURRENT_TIMESTAMP)')
    
    #Altername URLS for intensities: http://earthquake.usgs.gov/earthquakes/feed/v1.0/geojson.php
    request = urllib.request.urlopen("http://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/2.5_day.geojson")
    quake = json.loads(request.read().decode())
    request.close()
    quake = quake['features'][1] #select the latest quake
    qtitle = quake['properties']['title']
    mag = quake['properties']['mag']
    ids = quake['properties']['ids']
    updated = round(quake['properties']['time'] / 1000)
    updated = datetime.datetime.fromtimestamp(updated)
    ago = round((datetime.datetime.now() - updated).seconds / 60)
    lon = quake['geometry']['coordinates'][0]
    lat = quake['geometry']['coordinates'][1]



    quakestring = "Earthquake: M%s%s %s min" % (mag, rev_geocode(lat,lon), ago)
    quakestring = quakestring.ljust(32)

    return quakestring.encode()

def rev_geocode(lat,lon):
    results = Geocoder.reverse_geocode(lat,lon)
    #pdb.set_trace()
    country = results.raw[5]['address_components'][0]['short_name']
    state = results.raw[4]['address_components'][0]['short_name']
    city = results.raw[2]['address_components'][0]['short_name']

    return "%s, %s" % (city,state)

    
#LCD Command definitions
CLS = b'\xFE\x58'           #this will clear the screen of any text
HOME = b'\xFE\x48'          #place the cursor at location (1, 1)
CURSOR_POS = b'\xFE\x47'    #set the position of text entry cursor. Column and row numbering starts with 1 so the first position in the very top left is (1, 1)
CURSOR_BACK = b'\xFE\x4C'   #move cursor back one space, if at location (1,1) it will 'wrap' to the last position.
CURSOR_FWD = b'\xFE\x4D'    #move cursor forward one space, if at the last location location it will 'wrap' to the (1,1) position.

CURSOR_UNDERLINE_ON = b'\xFE\x4A'   #turn on the underline cursor
CURSOR_UNDERLINE_OFF = b'\xFE\x4B'  #turn off the underline cursor
CURSOR_BLINK_ON = b'\xFE\x53'       #turn on the blinking block cursor
CURSOR_BLINK_OFF = b'\xFE\x54'      #turn off the blinking block cursor

BACKLIGHT_ON=b'\xFE\x42'    #This command turns the display backlight on
BACKLIGHT_OFF=b'\xFE\x46'   #turn the display backlight off

CONTRAST = b'\xFE\x50'      #Set the display contrast. Add a byte value to this constant.
                            #In general, around 180-220 value is what works well.
                            #Setting is saved to EEPROM

BACKLIGHT_BRIGHTNESS = b'\xFE\x99'          #set the overall brightness of the backlight (the color component is set separately - brightness setting takes effect after the color is set)
BACKLIGHT_COLOR = b'\xFE\xD0'               #Sets the backlight to the red, green and blue component colors. The values of can range from 0 to 255 (one byte), last 3 bytes. This is saved to EEPROM
BACKLIGHT_ORANGE= b'\xFE\xD0\xFF\x01\x00'   #Sample orange color for the backlight
BACKLIGHT_TEAL= b'\xFE\xD0\x00\xFF\xFF'     #Sample teal color

AUTOSCROLL_ON = b'\xFE\x51'                 #this will make it so when text is received and there's no more space on the display
                                            #the text will automatically 'scroll' so the second line becomes the first line, etc.
                                            #new text is always at the bottom of the display

AUTOSCROLL_OFF = b'\xFE\x52'                #this will make it so when text is received and there's no more space on the display, the text will wrap around to start at the top of the display.
#END LCD Command Definitions

def cycle_colors(ser):

    r,g,b = 255,0,0

    step = 10
    
    for g in range(0,256,step):
        set_rgb(r,g,b)

    for r in range(255,-1,step*-1):
        set_rgb(r,g,b)

    for b in range(0,256,step):
        set_rgb(r,g,b)

    for g in range(255,-1,step*-1):
        set_rgb(r,g,b)

    for r in range(0,256,step):
        set_rgb(r,g,b)    

    for b in range(255,-1,step*-1):
        set_rgb(r,g,b)
    
def set_rgb(r,g,b)        :
        rgbstr = "%s,%s,%s" % (r,g,b)
        
        ser.write(BACKLIGHT_COLOR+bytes([r,g,b]))
        ser.write(CLS)
        ser.write(rgbstr.encode())

        time.sleep(0.15)
        

ser = serial.Serial(port='COM5', baudrate=9600)  # open first serial port

def init_lcd(ser):
    
    ser.write(CONTRAST + bytes([185])) #185 seems to be a good value for contrast
    ser.write(BACKLIGHT_BRIGHTNESS + bytes([122]))        
    ser.write(BACKLIGHT_TEAL)      # write a string
    ser.write(AUTOSCROLL_OFF)
    ser.write(CLS) #clear display

def scroll_text(line_one,line_two,speed,duration,ser):
#Duration may not be respected if it's shorter than (len(text)+32)*speed
    
    start_time = time.time()
    while (time.time()-start_time)<duration:
        ser.write(CLS)    
        ser.write(HOME)
        
        if len(line_one)>16 and len(line_two)>16:
            #Center the text in a bunch of white space so it scrolls nicely from one end to the other
            if len(line_one)>len(line_two):
                pad_length = len(line_one)+32
                line_one = line_one.center(pad_length," ") #Pad with spaces
                line_two = line_two.center(pad_length," ") #Pad with spaces
                wrap_len = len(line_one)-15 #Our LCD is 16 chars wide so limit to that
            else:
                pad_length = len(line_two)+32
                line_one = line_one.center(pad_length," ") #Pad with spaces
                line_two = line_two.center(pad_length," ") #Pad with spaces
                wrap_len = len(line_two)-15
            
            for i in range(0,wrap_len):
                ser.write(HOME)
                ser.write(line_one[0+i:16+i].encode())
                
                ser.write(CURSOR_POS+bytes([1,2]))
                ser.write(line_two[0+i:16+i].encode())
                
                if line_one[0+i:16+i] != " "*16:
                    time.sleep(speed)
        elif len(line_one)>16:
            pad_length = len(line_one)+32
            line_one = line_one.center(pad_length," ") #Pad with spaces        
            wrap_len = len(line_one)-15 #Our LCD is 16 chars wide so limit to that
            for i in range(0,wrap_len):
                ser.write(HOME)
                ser.write(line_one[0+i:16+i].encode())
                
                ser.write(CURSOR_POS+bytes([1,2]))
                ser.write(line_two.encode())

                if line_one[0+i:16+i] != " "*16:
                    time.sleep(speed)
        elif len(line_two)>16:
            pad_length = len(line_two)+32
            line_two = line_two.center(pad_length," ") #Pad with spaces        
            wrap_len = len(line_two)-15 #Our LCD is 16 chars wide so limit to that
            for i in range(0,wrap_len):
                ser.write(HOME)
                ser.write(line_one.encode())
                
                ser.write(CURSOR_POS+bytes([1,2]))
                ser.write(line_two[0+i:16+i].encode())
                if line_one[0+i:16+i] != " "*16:
                    time.sleep(speed)
            
        else:
            ser.write(line_one.encode())
            ser.write(CURSOR_POS+bytes([1,2]))
            ser.write(line_two.encode())



init_lcd(ser)
##while(1):
##    ser.write(get_weather())
##    time.sleep(1)
##    ser.write(get_quake_data())
##    time.sleep(5)


scroll_text("1234567890123456","123456789012345678",0.10,5,ser)
