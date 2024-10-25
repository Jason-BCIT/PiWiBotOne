from machine import Pin, PWM

class Tires():
    def __init__(self):
        self.right_forward = [ PWM(Pin(10, Pin.OUT)), PWM(Pin(11, Pin.OUT)) ]
        self.right_back = [ PWM(Pin(8, Pin.OUT)), PWM(Pin(9, Pin.OUT)) ]

        self.left_forward = [ PWM(Pin(20, Pin.OUT)), PWM(Pin(21, Pin.OUT)) ]
        self.left_back = [ PWM(Pin(18, Pin.OUT)), PWM(Pin(19, Pin.OUT)) ]

        for i in self.left_forward:
            i.freq(500)
            i.duty_u16(0)

        for i in self.left_back:
            i.freq(500)
            i.duty_u16(0)

        for i in self.right_forward:
            i.freq(500)
            i.duty_u16(0)

        for i in self.right_back:
            i.freq(500)
            i.duty_u16(0)


    def apply_power(self, left_forward, left_back, right_forward, right_back):
        print("Applying Power")
        for i in self.left_forward:
            #i.duty_u16(left_forward)
            i.duty_u16(32000)

        for i in self.left_back:
            #i.duty_u16(left_back)
            i.duty_u16(32000)
            
        for i in self.right_forward:
            #i.duty_u16(right_forward)
            i.duty_u16(32000)

        for i in self.right_back:
            i.duty_u16(right_back)
            #i.duty_u16(32000)
