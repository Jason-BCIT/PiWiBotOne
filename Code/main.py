#check to see if a button is pressed... if yes, connect to network defined in wifi.py, else establish Access Point defined in wifi_AP.py
from machine import Pin, ADC
Buttons=ADC(Pin(28))
if (Buttons.read_u16()>2000):
    import wifi as wifi
    print("Joining Wifi Network")
else:
    import wifi_AP as wifi
    print("Establishing Access Point -- Press and Hold a Button on Startup to Join Network")


import time
import tires
from machine import Pin

from ws_connection import ClientClosedError
from ws_server import WebSocketServer, WebSocketClient


LED_left = Pin(2, mode=Pin.OUT, value=1)
LED_right = Pin(3, mode=Pin.OUT, value=1)

tires = tires.Tires()
deadline = time.ticks_add(time.ticks_ms(), 300)

class TestClient(WebSocketClient):
    def __init__(self, conn):
        super().__init__(conn)

    def process(self):
        try:
            msg = self.connection.read()
            if not msg:
                return
            msg = msg.decode("utf-8")
            msg = msg.split("\n")[-2]
            msg = msg.split(" ")
            
            deadline = time.ticks_add(time.ticks_ms(), 300)
            print(msg[0]," X:",int(msg[1])," Y:",int(msg[2]))
            
            if msg[0]=="LED_Left":
                LED_left.value(int(msg[1]))
                print("LED_left=",int(msg[1]))
            
            if msg[0]=="LED_Right":
                LED_right.value(int(msg[1]))
                print("LED_right=",int(msg[1]))
                
            if msg[0]=="stick1":
                JoyY=int(msg[2])
                if ((JoyY<5) and (JoyY>-5)):  #deadband
                    JoyY=0
                    
                JoyX=int(msg[1])
                if ((JoyX<5) and (JoyX>-5)):  #deadband
                    JoyX=0
                
                MotorL=-JoyY+JoyX
                if (MotorL>128): MotorL=128
                if (MotorL<-128): MotorL=-128
                
                MotorR=-JoyY-JoyX
                if (MotorR>128): MotorR=128
                if (MotorR<-128): MotorR=-128
                
                print("MotorL= ",MotorL,"  MotorR= ",MotorR)
                      
                tires.apply_power(int(MotorL), int(MotorR),0,0)
                      
        except ClientClosedError:
            print("Connection close error")
            self.connection.close()
            #cleanup GPIO settings here
        except e:
            print("exception:" + str(e) + "\n")
            #cleanup GPIO settings here
            raise e
        except KeyboardInterrupt:
            print("Remember to write the code to clean up your GPIO pins on program interruption.")

                


class TestServer(WebSocketServer):
    def __init__(self):
        super().__init__("index_edited.html", 100)

    def _make_client(self, conn):
        return TestClient(conn)

wifi.run()

server = TestServer()
server.start()

while True:

    server.process_all()
    if time.ticks_diff(deadline, time.ticks_ms()) < 0:
        tires.apply_power(0,0,0,0)
        deadline = time.ticks_add(time.ticks_ms(), 100000)


            
server.stop()