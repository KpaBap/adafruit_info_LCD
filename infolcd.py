#!/usr/bin/python3
import serial
import urllib.request, urllib.parse, urllib, xml.dom.minidom, urllib.error, datetime
import json, time, sqlite3
#from pygeocoder import Geocoder

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
        line_one = city
        line_two = "%sF %sC Hum: %s" % (temp_f, temp_c, humidity)
        return line_one, line_two
    
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
    quake = quake['features'][0] #select the latest quake
    qplace = quake['properties']['place']
    mag = quake['properties']['mag']
    ids = quake['properties']['ids']
    updated = round(quake['properties']['time'] / 1000)
    updated = datetime.datetime.fromtimestamp(updated)
    ago = round((datetime.datetime.now() - updated).seconds / 60)
    lon = quake['geometry']['coordinates'][0]
    lat = quake['geometry']['coordinates'][1]



    line_one = "Earthquake: M%s" % (mag)
    line_two = "%s min ago %s" % (ago, qplace)
    
    

    return line_one, line_two

def rev_geocode(lat,lon):
    results = Geocoder.reverse_geocode(lat,lon)
    pdb.set_trace()
    country = results.raw[5]['address_components'][0]['short_name']
    state = results.raw[4]['address_components'][0]['short_name']
    city = results.raw[2]['address_components'][0]['short_name']

    return "%s, %s" % (city,state)


import datetime, urllib.request
import json

def get_nhl_live_games(ser,long_names=False,speed=5):


    

    today = datetime.date.today().strftime("%Y-%m-%d")
    url = "http://live.nhle.com/GameData/GCScoreboard/{}.jsonp".format(today)
    request = urllib.request.urlopen(url)
    data = request.read().decode()[15:-2]
    data = json.loads(data)
    
    if long_names:
        name_suffix = 'common'
    else:
        name_suffix = 'a'
    
    games = []
    for game in data['games']:
        #pdb.set_trace()
        if not game['bsc']:
            start = game['bs'].replace(':00 ', ' ')
            gametxt_one = "{} - {}".format(game['at%s' % name_suffix],
                                               game['ht%s' % name_suffix])
            gametxt_two = "\r({} ET)".format(start.center(11," "))
            gametxt_one = gametxt_one.center(15," ")
        else:
            gametxt_one = "{} {} - {} {}".format(game['at%s' % name_suffix],
                                                  game['ats'],
                                                  game['hts'],
                                                  game['ht%s' % name_suffix])
            
            gametxt_two = "\r({})".format(game['bs'].center(14," "))

            gametxt_one = gametxt_one.center(15," ")
            
        games.append(gametxt_one+gametxt_two)

    for game in games:
        ser.write(CLS)
        ser.write(HOME)
        
        ser.write(game.encode())
        alternate_fade(ser,*RGB_TEAL) #TEAM COLORS
        time.sleep(speed)

    return
        
    #line_one = " | ".join(games[0:(len(games)%2+len(games)//2)])
    #line_two = " | ".join(games[len(games)//2+len(games)%2:])                            
    #return line_one, line_two


    
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
BACKLIGHT_RED= b'\xFE\xD0\xFF\x00\x00'
BACKLIGHT_GREEN= b'\xFE\xD0\x00\xFF\x00'
AUTOSCROLL_ON = b'\xFE\x51'                 #this will make it so when text is received and there's no more space on the display
                                            #the text will automatically 'scroll' so the second line becomes the first line, etc.
                                            #new text is always at the bottom of the display
RGB_RED = (255,0,0)
RGB_GREEN = (0,255,0)
RGB_BLUE = (0,0,255)
RGB_TEAL = (0,255,255)
RGB_ORANGE=(255,1,0)
RGB_PURPLE=(255,0,255)

AUTOSCROLL_OFF = b'\xFE\x52'                #this will make it so when text is received and there's no more space on the display, the text will wrap around to start at the top of the display.
#END LCD Command Definitions

def alternate_fade(ser,r,g,b):
    rgb_dict = ser.cur_color
    steps = 255

      
    new_rgb = {"R":r,"G":g,"B":b}
    if rgb_dict == new_rgb: return

    if rgb_dict['R'] > new_rgb['R']:
        r_step = -1*((rgb_dict['R']-new_rgb['R'])/steps)
    elif rgb_dict['R'] == new_rgb['R']:
        r_step = 0
    elif rgb_dict['R'] < new_rgb['R']:
        r_step = 1*((new_rgb['R']-rgb_dict['R'])/steps)

    if rgb_dict['G'] > new_rgb['G']:
        g_step = -1*((rgb_dict['G']-new_rgb['G'])/steps)
    elif rgb_dict['G'] == new_rgb['G']:
        g_step = 0
    elif rgb_dict['G'] < new_rgb['G']:
        g_step = 1*((new_rgb['G']-rgb_dict['G'])/steps)

    if rgb_dict['B'] > new_rgb['B']:
        b_step = -1*((rgb_dict['B']-new_rgb['B'])/steps)
    elif rgb_dict['B'] == new_rgb['B']:
        b_step = 0
    elif rgb_dict['B'] < new_rgb['B']:
        b_step = 1*((new_rgb['B']-rgb_dict['B'])/steps)
    
    for faded_color in range(0,steps):
        r = rgb_dict['R']+int(round(r_step*faded_color,0))
        g = rgb_dict['G']+int(round(g_step*faded_color,0))
        b = rgb_dict['B']+int(round(b_step*faded_color,0))
        #print (r,g,b)
        
        try:
            set_lcd_color(ser,r,g,b)
            time.sleep(0.004)
        except:
            set_lcd_color(ser,new_rgb['R'],new_rgb['G'],new_rgb['B'])
    set_lcd_color(ser,new_rgb['R'],new_rgb['G'],new_rgb['B'])

def fade_to_color(ser,r,g,b):
    rgb_dict = ser.cur_color
    sorted_keys = sorted(rgb_dict,key=rgb_dict.get,reverse=True)

    step_one = 1
    low_limit = 70
    br_low_limit = 0
    br = 255
    
    step_two = rgb_dict[sorted_keys[1]]//((rgb_dict[sorted_keys[0]]-low_limit)//step_one)
    step_three = rgb_dict[sorted_keys[2]]//((rgb_dict[sorted_keys[0]]-low_limit)//step_one)
    br_step = 255//((rgb_dict[sorted_keys[0]]-br_low_limit)//step_one)

    #pdb.set_trace()

    for faded_color in range(rgb_dict[sorted_keys[0]]-step_one,low_limit,step_one*-1):
        rgb_dict[sorted_keys[0]] = faded_color
        rgb_dict[sorted_keys[1]] -= step_two
        rgb_dict[sorted_keys[2]] -= step_three
        br -= br_step
        set_lcd_color(ser,rgb_dict['R'],rgb_dict['G'],rgb_dict['B'])
        
        time.sleep(0.01)
        #print(rgb_dict)
        
    #print("FADE DOWN COMPLETE")
    rgb_dict = {"R":r,"G":g,"B":b}
    sorted_keys = sorted(rgb_dict,key=rgb_dict.get,reverse=True)

    step_two = rgb_dict[sorted_keys[1]]//((rgb_dict[sorted_keys[0]]-low_limit)//step_one)
    step_three = rgb_dict[sorted_keys[2]]//((rgb_dict[sorted_keys[0]]-low_limit)//step_one)

    rgb_dict[sorted_keys[1]] = 0
    rgb_dict[sorted_keys[2]] = 0
    
    for faded_color in range(low_limit,rgb_dict[sorted_keys[0]],step_one):
        rgb_dict[sorted_keys[0]] = faded_color
        rgb_dict[sorted_keys[1]] += step_two
        rgb_dict[sorted_keys[2]] += step_three
        br +=br_step
        
        try:
            set_lcd_color(ser,rgb_dict['R'],rgb_dict['G'],rgb_dict['B'])
            ser.write(BACKLIGHT_BRIGHTNESS+bytes([br]))
            
        except:
            set_lcd_color(ser,r,g,b)
        time.sleep(0.01)
        #print(rgb_dict)
    #set_lcd_color(ser,0,0,0)
        
def set_lcd_color(ser,r,g,b):
    ser.cur_color = {"R":r,"G":g,"B":b}
    ser.write(BACKLIGHT_COLOR+bytes([r,g,b]))
    
def cycle_colors(ser):

    r,g,b = 255,0,0

    step = 5
    
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
        



def init_lcd(ser):
    ser.cur_color = {"R":0,"G":0,"B":0}
    
    ser.write(CONTRAST + bytes([227])) #185 seems to be a good value for contrast
    ser.write(BACKLIGHT_BRIGHTNESS + bytes([255]))        
    #ser.write(BACKLIGHT_TEAL)      # Go SHARKS
    
    ser.write(AUTOSCROLL_OFF)
    ser.write(CLS) #clear display
    
    set_lcd_color(ser,128,128,128)

def scroll_text(ser,speed=0.36,duration=0,color=RGB_GREEN,line_one="",line_two=""):
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
                alternate_fade(ser,*color)
                
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
                alternate_fade(ser,*color)
                
                if line_one[0+i:16+i] != " "*16:
                    time.sleep(speed)
            
        else:
            ser.write(line_one.encode())
            ser.write(CURSOR_POS+bytes([1,2]))
            ser.write(line_two.encode())
            alternate_fade(ser,*color)
            time.sleep(duration) #dont do anything else for the duration, no need to redraw
            return

        
ser = serial.Serial(port='/dev/ttyACM0', baudrate=9600)  # open first serial port
init_lcd(ser)


##while(1):
##    ser.write(CLS+"ALTERNATE FADE\rBLAH BLAH BLAH".encode())
##    time.sleep(2)
##    alternate_fade(ser,*RGB_ORANGE)
##
##    time.sleep(2)
##    alternate_fade(ser,*RGB_TEAL)
##    time.sleep(2)
##    alternate_fade(ser,*RGB_PURPLE)
##    time.sleep(2)
##    alternate_fade(ser,*RGB_GREEN)
##    time.sleep(2)
##    alternate_fade(ser,*RGB_BLUE)
##    time.sleep(2)
##    alternate_fade(ser,*RGB_RED)
while(1):

    scroll_text(ser,0.35,5,RGB_PURPLE,*get_weather())

    scroll_text(ser,0.30,1,RGB_RED,*get_quake_data()) 
    get_nhl_live_games(ser,speed=3)             #NHL sets its own color
    
##while(1):
##    ser.write(get_weather())
##    time.sleep(1)
##    ser.write(get_quake_data())
##    time.sleep(5)


