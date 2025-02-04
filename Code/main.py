#This program executes upon startup. It is the main program that calls all the other functions for running the PiWiBot
#When running PiWiBot code from Thonny, this is the program that you need to run!

#The code for this project is located at: https://github.com/Jason-BCIT/PiWiBotOne    Check there for updates and feel free to fork/copy all you want.
#This code is based on "CrawlSpaceBot" by Adrian Cruceru, at https://github.com/AdrianCX/crawlspacebot   Published under MIT License (see license.py for details)

print("---------------------")
print("STARTING PiWiBot Code")
print("---------------------")
#------------------------------------------------------------------------------------------------------------------------------------------
#check to see if a button is pressed... if yes, connect to network defined in wifi.py, else establish Access Point defined in wifi_AP.py
from machine import Pin, ADC				#imports Pin mapping (which pin to which number) and Analog Digital Convertor functions from the MicroPython machine module (a module in micropython is like a library in the Arduino IDE)

Buttons=ADC(Pin(28))
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

LED_left = Pin(2, mode=Pin.OUT, value=1)			#The Left Hand "Headlight" is connected to pin 2, is an OUTPUT, and starts out turned ON
LED_right = Pin(3, mode=Pin.OUT, value=1)			#The Right Hand "Headlight" also starts out turned on, as the value is set to one

motors = drive_motors.Motors()						#creates a motors object for the two drive motors. Refers to the "drive_motors.py" file, imported above
deadline = time.ticks_add(time.ticks_ms(), 300)		#reads the system clock and creates a deadline for 300 ms in the future. This is used to stop the robot if it loses communication with the controller

#if you're following the order of execution of this program, it now jumps all the way down to the wifi.run statement near the bottom of this file. Then it begins the infinite "while True" loop which runs the robot
#the infinite loop continuously calls the "server.process_all" function which is defined towards the end of the "ws_server.py" file. It then refers the program execution back to the process function, defined below

class TestClient(WebSocketClient):					#this defines a class to manage the websocket communication with the javascript code (in webpage.html) that runs on the phone/tablet/PC controlling the robot
    def __init__(self, conn):						#the class refers to the WebSocketClient function that is imported from the "ws_server.py" file earlier in this program
        super().__init__(conn)						#this is some weird object-oriented programming stuff that I'm still trying to figure out... but it has to do with how the class is initialized when you first set it up

    def process(self):								#This function gets called repeatedly to check for data from the controller and set values based on what the data contains. It exists inside the TestClient class, defined above
        try:										#"try" is Python's way to say, "do this, but if there is an error, break out of the command and report the error back so we can handle it"
            msg = self.connection.read()			#This tries to read the connection
            if not msg:
                return								#but if there is no data there, it ends the function and returns to wherever the function was called from
            msg = msg.decode("utf-8")				#this interprets the data as a standard text file
            msg = msg.split("\n")[-2]				#this splits the data wherever a "new line" character is
            msg = msg.split(" ")					#this splits the data wherever a "space" character is
            
            #The data that is being split comes from the javascript running on the browser being used to drive the robot (see webpage.html)
            #The usual format will have the name of the object that created the data in the msg[0] field
            #For a joystick object the msg[1] field will contain the X value of the joystick and msg[2] will contain the Y value
            #For a slider the position of the slider will be reported in msg[1]
            #For an LED button, the desired value for the LED (1=HIGH, 0=LOW) will be in msg[1]
            
            deadline = time.ticks_add(time.ticks_ms(), 300)			#since data was successfully received (or we wouldn't be at this point in the code) extend the deadline for another 300ms
            print("msg[0]= ",msg[0]," msg[1]= ",int(msg[1])," msg[2]= ",int(msg[2]))		#print the first three items of data received. The first item will be the name of the object that created the data... eg "stick1" or "LED_Left"
            
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
                
                #JoyX=JoyX/2							#if your robot's turning is too sensitive, you can dampen the turn response by reducing the value of JoyX. Uncomment this command to cut the sensitivity in half
                
                MotorL=-JoyY+JoyX						#these lines "mix" the JoyX and JoyY values to create the speeds for each motor. For more details google "Joystick mixing for arcade drive"
                if (MotorL>128): MotorL=128				#the motor's speed settings range from -128 (full reverse) to +128 (full forward). Zero is "stop".
                if (MotorL<-128): MotorL=-128			#these two statements make sure that the speed never exceeds these limits
                
                MotorR=-JoyY-JoyX						#these lines create the speed value for the right motor using a similar technique to the left motor, above
                if (MotorR>128): MotorR=128
                if (MotorR<-128): MotorR=-128
                
                print("MotorL= ",MotorL,"  MotorR= ",MotorR)		#print out the values for debugging
                      
                motors.apply_power(int(MotorR), int(MotorL),0,0)    #send the values to the motors.apply_power function (located in the "drive_motors.py" file)
                                                                    #it is possible to send four values to the motors.apply_power function, so future expansion to four drive motors is possible
            if msg[0]=="Slider_1":
                slider=int(msg[2])					#convert the slider message to an integer number
                if ((slider<15) and (slider>-15)):  			#this is the "deadband". It means that the slider doesn't have to be perfectly centered in order for the motors to turn off
                    slider=0
                if (slider>128): slider=128				#the motor's speed settings range from -128 (full reverse) to +128 (full forward). Zero is "stop".
                if (slider<-128): slider=-128			#these two statements make sure that the speed never exceeds these limits
                print("Slider1= ",slider)
                motors.set_Motor3(slider)
            
            if msg[0]=="stick2":
                motors.set_Servo1(int(msg[1]))
            
        except ClientClosedError:					#at the beginning of this function there is a "try" command. In the event that an error occurs during the function, it will come here to handle common errors
            print("Connection close error")			#the connection to the webpage was closed. Perhaps the browser was closed?
            self.connection.close()					#close the connection
            #cleanup GPIO settings here
            motors.apply_power(0,0,0,0)				#stop the motors
            motors.set_Motor3(0)
       
        except KeyboardInterrupt:					#this will trigger if you send a command from Thonny to stop program execution
            print("Keyboard interrupt over serial connection.")
            motors.apply_power(0,0,0,0)				#stop the motors
            motors.set_Motor3(0)
            sys.exit(0)
    
class TestServer(WebSocketServer):					#this defines the TestServer class and refers to the WebSocketServer class imported from the "ws_server.py" file in this package
    def __init__(self):								#this runs once, on initialization of an object of this class
        super().__init__("webpage.html", 100)		#and references the "webpage.html" file that will be served to the phone/tablet/PC browser that connects to the PiWiBot

    def _make_client(self, conn):					
        return TestClient(conn)

wifi.run()			#depending on whether the button was pressed on startup, either the "wifi.py" file or the "wifi_AP.py" file will be imported and named "wifi"
                    # each of these files has a "run" function. To follow the code execution, take a look for the "run" function in either wifi.py or wifi_AP.py

server = TestServer()	#the class "TestServer" is defined, above. When this class is assigned to the name "server", the __init__ function will execute, so the code will jump to the "ws_server.py" file
server.start()			# the server object, created in the last command, has a function called "start". You can see the definition of this function in the "ws_server.py" file

while True:						#Infinite Loop! The indented code, below, will keep cycling around until you tell it to stop, or turn the robot's power off
    
    server.process_all()										#the "server" object was created about six lines above here. The "process_all" function is included in the file "ws_server.py"
    if time.ticks_diff(deadline, time.ticks_ms()) < 0:			#checks to see if the "deadline" time is less than the current time. If it is, then the deadline has passed and we have had a communications problem
        print("Data link not responding. Motors turned off.")	# if there is a communication problem, report the problem
        motors.apply_power(0,0,0,0)								# turn off the motors
        motors.set_Motor3(0)
        deadline = time.ticks_add(time.ticks_ms(), 10000)		# and create a longer deadline so that the PicoW and the control device have a chance to re-establish communication
            
server.stop()				#this code will execute should something happen to break out of the main loop. But it may never actually execute.