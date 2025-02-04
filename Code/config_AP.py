#The default startup option for the PiWiBot is to host a WiFi access point
#You can change the name of the Access Point ("AP") below
#It is recommended to change the name of the AP so that your robot is not confused with others

#The default setting for the PiWiBot is to create an open network (no password)
#If you want to password protect your robot's AP, add the password between the quote marks, below
#These settings are used in the wifi_AP.py file for establishing your access point and setting the parameters

WIFI_SSID='PiWiBot'
WIFI_PASSWORD=''

#A flag to tell the rest of the software that you are operating in Access Point mode (ie, not connected to a home network)
WIFI_AP_MODE=True