#This program executes upon startup. It is the main program that calls all the other functions for running the PiWiBot
#When running PiWiBot code from Thonny, this is the program that you need to run!

#The code for this project is located at: https://github.com/Jason-BCIT/PiWiBotOne    Check there for updates and feel free to fork/copy all you want.
#This code is based on "CrawlSpaceBot" by Adrian Cruceru, at https://github.com/AdrianCX/crawlspacebot   Published under MIT License (see license.py for details)

print("---------------------")
print("STARTING PiWiBot Code")
print("---------------------")

#------------------------------------------------------------------------------------------------------------------------------------------
#check to see if a button is pressed... if yes, connect to network defined in wifi.py, else establish Access Point defined in wifi_AP.py

from machine import Pin, ADC, reset				#imports Pin mapping (which pin to which number) and Analog Digital Convertor functions from the MicroPython machine module (a module in micropython is like a library in the Arduino IDE)
import os					#used for managing file functions and creating a debugging file on the pico
from sys import exit
Buttons=ADC(Pin(28))		#the pin that the buttons are connected to... used to determine if a button is pressed

# ***** The code normally reads ">2000" so that it connects to wifi when button is pressed... this has been changed
if (Buttons.read_u16()>2000):				#if the button is pressed when this code executes (once, at startup) it will force the robot to connect to your home network
    import wifi as wifi						#imports the "wifi.py" file from this package and names it wifi. This gives the parameters for connecting to your home network.
    print("Joining Wifi Network")
else:										#if the button is not pressed the robot will establish a WiFi access point. This is the default setting
    import wifi_AP as wifi					#imports the "wifi_AP.py" file from this package and names it wifi. This gives the parameters for establishing an access point.
    print("Establishing Access Point -- Press and Hold a Button on Startup to Join a home Network")
    #although it prints "Establishing Access Point", and "Joining Wifi Newtork" in this section of code, the actual setup of the AP or joining of the home network doesn't happen until you hit the wifi.run() command, about 90 lines
    # below this point. This is because the next 90 lines are used for setting up the functions that will be called by the main loop of the program. So if you're following the code step-by-step... jump ahead to where it says "wifi.run()"
#-------------------------------------------------------------------------------------------------------------------------------------------

import time										#a micropython library to manage time functions
import drive_motors								#the "drive_motors.py" file that is part of this package. It contains the instructions for setting up the motors and making them run.

from ws_connection import ClientClosedError				#imports the ClientClosedError function from the "ws_connection.py" file contained in this package
from ws_server import WebSocketServer, WebSocketClient	#imports two functions from the "ws_server.py" file contained in this package

from machine import I2C								#for display and other I2C devices
from ssd1306 import SSD1306_I2C
i2c=I2C(0,sda=Pin(4), scl=Pin(5), freq=800000)  #set up an i2c communication channel on pins 16 and 17

try:
    print("Connecting to OLED Display")
    oled = SSD1306_I2C(128, 64, i2c)  #connect to a 128 x 64 screen and call it oled
    OLED_installed = True 
except Exception as e:
    print("*** No OLED Display Connected ***")
    OLED_installed = False 
if OLED_installed:
    oled.fill(0)
    oled.text("Wifi: CanaBot",10,0)
    oled.text("http://",30,10)
    oled.text("192.168.4.1", 10,20)
    oled.show()

try:
    print("Connecting to VL53L0X ToF LIDAR Rangefinder")
    import VL53L0X						#rangefinder library
    tof = VL53L0X.VL53L0X(i2c)
    LIDAR_installed=True
except Exception as e:
    print("*** Cannot connect to VL53L0X LIDAR ***")
    LIDAR_installed=False
    
import neopixel
np = neopixel.NeoPixel(machine.Pin(1), 10)
np[0] = (32, 0, 0) # set to red, full brightness
np[1] = (0, 32, 0) # set to green, half brightness
np[2] = (0, 0, 32)  # set to blue, quarter brightness
pixel=0
np.write()

LED_left = Pin(2, mode=Pin.OUT, value=1)			#The Left Hand "Headlight" is connected to pin 2, is an OUTPUT, and starts out turned ON
LED_right = Pin(3, mode=Pin.OUT, value=1)			#The Right Hand "Headlight" also starts out turned on, as the value is set to one

fileNumber=0

for x in range(1,5):				#five little flashes to confirm the code has started
    LED_right.value(0)				#only runs once, on startup
    time.sleep(0.1)
    LED_right.value(1)
    time.sleep(0.1)
    print("Boombot is Waking Up!")

motors = drive_motors.Motors()						#creates a motors object for the two drive motors. Refers to the "drive_motors.py" file, imported above
deadline = time.ticks_add(time.ticks_ms(), 300)		#reads the system clock and creates a deadline for 300 ms in the future. This is used to stop the robot if it loses communication with the controller

#if you're following the order of execution of this program, it now jumps all the way down to the wifi.run statement near the bottom of this file. Then it begins the infinite "while True" loop which runs the robot
#the infinite loop continuously calls the "server.process_all" function which is defined towards the end of the "ws_server.py" file. It then refers the program execution back to the process function, defined below

def manage_file (mode):                #if mode=1 then search for a safe filename and open a new file, if mode=0 then close the file
    global fileNumber                #creating and opening the new file can take many 10's of ms, longer when searching for a unique filename
    global f
    global fileName
    
    if (mode==1):										#manage_file(1) creates a new log file
        fileName="DriveLog"+str(fileNumber)+".txt"       #this line creates a log file on the PicoW and overwrites the previous log file    
        #exists=False									#if you want to maintain a unique log file for each power up sequence, uncomment this code
        #while (exists==False):							#it will check to see if the file name you are creating already exists, and if it does
        #    try:										#then it will increment the file number by one and try again
        #       f = open(fileName, "x")					#just keep in mind that it will eventually fill up the PicoW's storage with log files
        #       exists = True							#so if you do uncomment this, remember to clean out the log files every few dozen runs
                
        #    except OSError:
        #       exists = False
        #        print(fileName," exists already")
        #        fileNumber=fileNumber+1
        #        fileName="Drive"+str(fileNumber)+".txt"
        
               
        f = open(fileName, "w")
        print(fileName)
        f.write("start driving\n")
        
    if (mode==0):									#manage_file(0) closes the existing log file
        f.write("All done. Controlled Exit from Code.")
        f.close()
    

class TestClient(WebSocketClient):					#this defines a class to manage the websocket communication with the javascript code (in webpage.html) that runs on the phone/tablet/PC controlling the robot
    def __init__(self, conn):						#the class refers to the WebSocketClient function that is imported from the "ws_server.py" file earlier in this program
        super().__init__(conn)						#this is some weird object-oriented programming stuff that I'm still trying to figure out... but it has to do with how the class is initialized when you first set it up
        self.last_packet_time=0
        self.buf = bytearray(256)   # preallocating a byte array to reduce memory management overhead which causes time delays each time we read the data from the webpage
      
    @micropython.native								#try running this faster by pre-compiling parts of it    
    def process(self):								#This function gets called repeatedly to check for data from the controller and set values based on what the data contains. It exists inside the TestClient class, defined above
        
        self.connection.write(str(time.ticks_ms()-self.last_packet_time))		#measures the time delay between the current execution of this loop and the previous execution of the loop and sends it to the controller
        self.last_packet_time=time.ticks_ms()										#using a websocket. You can see the data in Chrome's Dev Tools under the "Network" tab
                                                                                #this is currently under development to provide feedback from the robot directly to the web interface.
        
        try:													#"try" is Python's way to say, "do this, but if there is an error, break out of the command and report the error back so we can handle it"
            msg = self.connection.read()						#get the data for this websocket object
            if not msg:											#if there is no message then...
                #f.write("-")			#if there is no readable message quickly record a "-"
                #f.flush()				#these log file writes are commented out to save processing time
                return											# return to the line that called this function

            n = len(msg)										#this breaks the websocket data down into chunks for processing
            self.buf[:n] = msg  # copy into buffer
            websocket_message = self.buf[:n].decode("utf-8")
            msg = websocket_message.strip().split(" ")
                              
            #The data that is being split comes from the javascript running on the browser being used to drive the robot (see webpage.html)
            #The usual format will have the name of the object that created the data in the msg[0] field
            #For a joystick object the msg[1] field will contain the X value of the joystick and msg[2] will contain the Y value
            #For a slider the position of the slider will be reported in msg[1]
            #For an LED button, the desired value for the LED (1=HIGH, 0=LOW) will be in msg[1]
            
            deadline = time.ticks_add(time.ticks_ms(), 300)			#since data was successfully received (or we wouldn't be at this point in the code) extend the deadline for another 300ms
            print(msg[0]," X:",int(msg[1])," Y:",int(msg[2]))		#print the first three items of data received. The first item will be the name of the object that created the data... eg "stick1" or "LED_Left"
            
            #the commented out code below here provides enhanced data logging to a file on the pico. This takes time, however, so I have commented this code out for normal operation. Uncomment when debugging.
            #try:
            #    f.write("Message Decode Time="+str(time.ticks_ms())+","+str(msg[0])+","+str(msg[1])+","+str(msg[2])+"\n")
            #    f.flush()
            #except:
            #    print("Didn't record data")
            #    f.write("Didn't record data")
            #    f.flush()
                
            if msg[0]=="LED_Left":						#if the message came from the LED_Left object on the webpage
                LED_left.value(int(msg[1]))				#set the LED_left pin to the value of the next data element (expected to be 1 for HIGH and 0 for LOW)
                print("LED_left=",int(msg[1]))			#print the data over the serial monitor to help with debugging
            
            if msg[0]=="LED_Right":						#see LED_Left, above, for explanation
                LED_right.value(int(msg[1]))
                print("LED_right=",int(msg[1]))
                
            if msg[0]=="stick1":						#if the message came from the "stick1" object then we will mix the X and Y values and use them to control the robot's motors
                JoyY=int(msg[2])						#the data comes from the webpage as characters, so we use the "int" statement to turn it into an integer variable so that we can do math with it
                if ((JoyY<5) and (JoyY>-5)):  			#this is the "deadband". It means that the joystick doesn't have to be perfectly centered in order for the motors to turn off
                    JoyY=0								#so if the joystick is "close" to centre then just set it to zero. Want a bigger deadband? Increase the value in the previous line (default=5)
                    
                JoyX=int(msg[1])						#see the JoyY section, above, for explanation
                if ((JoyX<5) and (JoyX>-5)):  			#deadband
                    JoyX=0
                
                JoyX=JoyX/2							#if your robot's turning is too sensitive, you can dampen the turn response by reducing the value of JoyX. Uncomment this command to cut the sensitivity in half
                
                MotorL=-JoyY+JoyX						#these lines "mix" the JoyX and JoyY values to create the speeds for each motor. For more details google "Joystick mixing for arcade drive"
                if (MotorL>128): MotorL=128				#the motor's speed settings range from -128 (full reverse) to +128 (full forward). Zero is "stop".
                if (MotorL<-128): MotorL=-128			#these two statements make sure that the speed never exceeds these limits
                
                MotorR=-JoyY-JoyX						#these lines create the speed value for the right motor using a similar technique to the left motor, above
                if (MotorR>128): MotorR=128
                if (MotorR<-128): MotorR=-128
                
                print("MotorL= ",MotorL,"  MotorR= ",MotorR)		#print out the values for debugging
                      
                motors.apply_power(int(MotorR), int(MotorL),0,0)    #send the values to the motors.apply_power function (located in the "drive_motors.py" file)
                                                                    #it is possible to send four values to the motors.apply_power function, so future expansion to four drive motors is possible
                
            if msg[0]=="Slider_1":					#if the Slider_1 object on the web interface is the one returning a value
                slider=int(msg[2])					#convert the slider message to an integer number
                if ((slider<15) and (slider>-15)):  			#this is the "deadband". It means that the slider doesn't have to be perfectly centered in order for the motors to turn off
                    slider=0
                if (slider>128): slider=128				#the motor's speed settings range from -128 (full reverse) to +128 (full forward). Zero is "stop".
                if (slider<-128): slider=-128			#these two statements make sure that the speed never exceeds these limits
                print("Slider1= ",slider)				
                motors.set_Motor3(slider)			#this lets you use the slider to turn a motor on and leave it on... you could easily change this up to have the slider control a servo, of course
                                                    #or add addditional sliders to the web interface
            
            if msg[0]=="stick2":						#if the stick2 object is the one returning a value
                motors.set_Servo1(int(msg[1]))			#use the value in msg[1] to control the servo. For tank drive you could use this to control the right motor.


        except ClientClosedError:					#at the beginning of this function there is a "try" command. In the event that an error occurs during the function, it will come here to handle common errors
            print("Connection close error")			#the connection to the webpage was closed. Perhaps the browser was closed?
            self.connection.close()					#close the connection
            #cleanup GPIO settings here
            motors.apply_power(0,0,0,0)				#stop the motors
            f.write("ClientClosedError\n")
            f.flush

        except KeyboardInterrupt:					#this will trigger if you send a command from Thonny to stop program execution
            print("Keyboard interrupt over serial connection.")
            f.write("\nKeyboard interrupt over serial connection. \n")
            f.flush()
            motors.apply_power(0,0,0,0)				#stop the motors
            f.close()
            sys.quit()
            
        except:
            motors.apply_power(0,0,0,0)			#if an error occurred in the preceeding try, and it wasn't a ClientClosedError (from the website) or a Keyboard Interrupt, then flash the LEDs and complain
            for x in range(1,10):
                LED_right.value(1)
                time.sleep(0.1)
                LED_right.value(0)
                time.sleep(0.1)
            print("An Error occurred in the main loop")
            #f.write("An Error occured in the main loop\n")
            #f.flush()
    
class TestServer(WebSocketServer):					#this defines the TestServer class and refers to the WebSocketServer class imported from the "ws_server.py" file in this package
    def __init__(self):								#this runs once, on initialization of an object of this class
        super().__init__("webpage.html", 100)		#and references the "webpage.html" file that will be served to the phone/tablet/PC browser that connects to the PiWiBot

    def _make_client(self, conn):					
        return TestClient(conn)
    
manage_file(1)		#create a log file for troubleshooting
wifi.run()			#depending on whether the button was pressed on startup, either the "wifi.py" file or the "wifi_AP.py" file will be imported and named "wifi"
                    # each of these files has a "run" function. To follow the code execution, take a look for the "run" function in either wifi.py or wifi_AP.py

server = TestServer()	#the class "TestServer" is defined, above. When this class is assigned to the name "server", the __init__ function will execute, so the code will jump to the "ws_server.py" file
server.start()			# the server object, created in the last command, has a function called "start". You can see the definition of this function in the "ws_server.py" file

#*********************************************************************************************************************************************************************************************
while True:						#Infinite Loop! The indented code, below, will keep cycling around until you tell it to stop, or turn the robot's power off
    
    		
    server.process_all()     	#the "server" object was created about six lines above here. The "process_all" function is included in the file "ws_server.py"
                                #This object handles all of the communication and motor control.
    
    #this is a safety "timeout" routine to shut the motors down if communication is lost. For instance if you drive outside wifi range this should stop the robot from continuing to drive away from you.
    if time.ticks_diff(deadline, time.ticks_ms()) < 0:			#checks to see if the "deadline" time is less than the current time. If it is, then the deadline has passed and we have had a communications problem
        print("Data link not responding. Motors turned off.")	# if there is a communication problem, report the problem
        motors.apply_power(0,0,0,0)								# turn off the motors
        deadline = time.ticks_add(time.ticks_ms(), 10000)		# and create a longer deadline so that the PicoW and the control device have a chance to re-establish communication
     
    if LIDAR_installed:				# if the LIDAR Rangefinder is installed, measure the distance (up to 999mm)
        tof.start()
        distance=tof.read()
        if (distance>999):
            distance=999
        #print("Range:",distance," mm")
        tof.stop()
    else:
        distance=1		#place a small positive value in here as an error message
                        
    if OLED_installed:				#if the OLED display is installed, display the rangefinder distance
        oled.fill_rect(0,39,105,6,0)
        oled.rect(0,40,int(distance/8),4,1)
        oled.show()
    
    #update the Neopixel display with a rolling flash to give an idea of the refresh rate of this control loop
    #works just fine even if the Neopixel strip is not installed because the Neopixels give no feedback
    pixel=pixel+1
    if (pixel>8):
        pixel=0
    np[pixel]=(32,0,0)
    np[pixel-1]=(0,0,0)
    np.write()
    


    
server.stop()				#this code will execute should something happen to break out of the main loop. But it may never actually execute.