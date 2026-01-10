#These settings are for connecting to your home network
#Hold down a button on startup to choose the home network option
#When you connect to your home network, the PicoW will print the IP address over the serial monitor
#Navigate to the IP address using a web browser on any computer connected to the network
#This allows you to use the desktop version of Chrome to inspect/debug the web page in the "index_edited.html" file

WIFI_SSID='YOUR_SSID'
WIFI_PASSWORD='YOUR_WIFI_PASSWORD'
#mDNSname matters because it identifies your robot to a local network. If your mDNSname is "PiWiBot" then your web browser
#should find the robot at http://PiWiBot.local    This only works with web browsers on the same network as the robot.
mDNSname="PiWiBot"         #you may have to do a complete, hard, power down of the pico to fully reset the mDNSname to a new name
# Set up a wireless hotspot with WIFI_SSID/WIFI_PASSWORD above, useful for testing
WIFI_AP_MODE=False