#These settings are for connecting to your home network
#Hold down a button on startup to choose the home network option
#When you connect to your home network, the PicoW will print the IP address over the serial monitor
#Navigate to the IP address using a web browser on any computer connected to the network
#This allows you to use the desktop version of Chrome to inspect/debug the web page in the "index_edited.html" file

WIFI_SSID='YourHomeWiFiSSID'
WIFI_PASSWORD='YourHomeWiFiPassword'

# Set up a wireless hotspot with WIFI_SSID/WIFI_PASSWORD above, useful for testing
WIFI_AP_MODE=False