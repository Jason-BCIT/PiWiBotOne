#These functions will only be executed when you start the PiWiBot in 'home network' mode by holding down a button on startup
#This file sets up the functions for connecting to a home network

import network						#this is a micropython module (aka library) that provides netowrk drivers and routing configuration
import socket						#this is a micropython module that knows how to talk to the "socket" interface available on most operating system for transferring data over a network connection
import time							#this is a micropython module that manages time functions
import re							#this is a micropython module that manages "regular expression" operations, which means that using the "\" character can be used to help send control codes and non-printable characters
import config						#this is the "config.py" file included in this package, and contains the information needed for connecting to your home network, such as the SSID and Password
import machine						#this is a micropython module that contains information about the microcontroller board, such as which pin corresponds to which pin number

def wait_wlan(wlan):		#this is a function to wait for the PicoW to connect to your home network. It is called from "connect_wlan()", lower in this file
    max_wait = 10			#this sets a limit on how many times the PicoW will try to connect to the home network... usually it connects in the first few tries.
    while max_wait > 0:		#keep trying the indented code, below, until you run out of tries
        if wlan.status() < 0 or wlan.status() >= 3:			#this checks the status of the connection. On the PicoW, status codes less than zero, 4 or 5 indicate errors. 3 Indicates a successful connection with IP address issued
            break											#so if you have either established a successful connection, OR have a known connection error, then stop trying to connect
        max_wait -= 1									#but if the code is 0 (not connected),1 (in the process of connecting), or 2 (connected, but haven't received an IP address) then try again
        print('waiting for connection...')				#it seems the codes, above, are not MicroPython standard, but are determined by the CYW43 wifi module on the PicoW... feel free to investigate further!! :-)
        time.sleep(1)									#but wait a second before trying again, to give the Access Point time to process the connection request

    if wlan.status() != 3:								#a status of 3 indicates a successful connection to the network, with an IP address received by the PicoW	
        print("Failed setting up wifi, will restart in 30 seconds")		#so if we haven't seen this after ten tries, deliver an error message, wait a while, and try again
        time.sleep(30)									#of course the error message is only helpful if your PicoW is connected to a serial port to display the message... perhaps some kind of blinking LED code could be written here
        machine.reset()

def connect_wlan():							#this function is called when the run function, below, is executed. It connects to a wifi network, and returns the details of that connection as part of the wlan object
    wlan = network.WLAN(network.STA_IF)		#this calls MicroPython's network module ("library") and asks it to create a network connection in "STAtion" mode (as a client connected to a router)
    wlan.active(False)						#this turns off any existing wifi connections
    wlan.disconnect()						#and disconnects from them so that the wifi module forgets any information from previous connections
    
    wlan.active(True)						#this establishes a new connection
    wlan.connect(config.WIFI_SSID, config.WIFI_PASSWORD) #using the network name and password that you define in "config.py"

    wait_wlan(wlan)							#this calls the "wait_wlan" function, defined above, to wait for the network connection to be made and the IP address to be issued
    
    print('connected to wifi:', config.WIFI_SSID, 'with ip = ', wlan.ifconfig()[0])		#when the connection is made and the IP address is secured, print out the data so you know what IP address to connect your browser to
    return wlan					#return the wlan information so that other parts of the program can use it

def run():
    wlan = connect_wlan() if not config.WIFI_AP_MODE else setup_ap() #this checks to see if we are in Station mode (connected to a network) or AP mode (hosting a network) and passes the wlan information to the correct routines
