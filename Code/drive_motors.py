from machine import Pin, PWM		#This imports the Pin definitions and PWM routines from the MicroPython machine module (aka 'library')

#Each motor requires two pins. One controls speed (that's the PWM pin) and one controls the direction. 

class Motors():									#this creates a class for the motors. The class includes both the definition of which pins are for which motor, and the apply_power function to set the speeds of the two main drive motors
    def __init__(self):							#the __init__ function executes when an object of this class is created
        self.motor1_dir=Pin(12, mode=Pin.OUT)	#this sets motor1's direction pin to be on GPIO Pin 12 and assigns it as a High/Low OUTPUT (much like the pinMode command in the Arduino IDE)	DEFAULT VALUE is 12
        self.motor1_PWM=PWM(Pin(13))			#this sets motor1's speed pin to be on GPIO Pin 13, and sets it as a PWM output. This will allow for variable motor speeds.	DEFAULT VALUE is 13
        self.motor1_PWM.freq(5000)				#this sets the frequency of the PWM output to 5000Hz.
        self.motor1_PWM.duty_u16(00000)			#and this sets the duty cycle of the PWM output on the pin to 0... so the pin is always LOW to start.

        self.motor2_dir=Pin(14, mode=Pin.OUT) #Motor two works similar to motor1, above. Default Value is 14
        self.motor2_PWM=PWM(Pin(15)) #Default Value is 15
        self.motor2_PWM.freq(5000)
        self.motor2_PWM.duty_u16(00000)
        
        self.motor3_dir=Pin(19, mode=Pin.OUT) #Motor two works similar to motor1, above. Default Value is 19
        self.motor3_PWM=PWM(Pin(18)) #Default Value is 18
        self.motor3_PWM.freq(5000)
        self.motor3_PWM.duty_u16(00000)
        
        self.motor4_dir=Pin(17, mode=Pin.OUT) #Motor two works similar to motor1, above. Default Value is 17
        self.motor4_PWM=PWM(Pin(16)) #Default Value is 16
        self.motor4_PWM.freq(5000)
        self.motor4_PWM.duty_u16(00000)

        self.servo1=PWM(Pin(21))  #Default value is 21
        self.servo1.freq(50)		#send a signal every 20mS
        #self.servo1.duty_ns(1000000) #one million nanoseconds is one ms, the netral position for a servo
        self.servo1.duty_u16(1000)
        
        #self.servo2=PWM(Pin(20))  #Default value is 20

#When the program is running it will call motors.apply_power, and pass the following information to this function

    def apply_power(self, MotorL, MotorR, Motor3, Motor4): 						#self refers to the object itself... yeah, I don't really get it either, but the other four variables are passed from the function call and they make sense
        print("Applying Power ",MotorL," ",MotorR," ",Motor3," ",Motor4)		# because they are the motor speed values on a scale of -128(reverse) to +128(forward). Zero is "stop". Motor3 and Motor4 are for future expansion if needed.
        Motor_Start=25000	#Each motor/gearbox combo has a bit of drag. This is the pwm threshold where the motors actually get enough power to overcome inertia and begin to turn. Default is 25000, but feel free to tweak this.
                            #In the Arduino IDE, the analogWrite function allows PWM values from 0-255 because it is 8 bit resolution, but PWM on the PicoW has 16 bit resolution, so the range of values is 0-65,535.
                            #so a Motor_Start value means that when you start out, the motor immediately jumps to about 40% of "full speed" (25K/65K=40%). Anything less might not move because of the drag of the gearbox and motor bearings.
        
        MotorL=MotorL*1		#if motor turns backwards, set this to -1... or change how you have your motors plugged in!
        MotorR=MotorR*-1		#if motor turns backwards, set this to 1... or change how you have your motors plugged in!
        
        if (MotorL==0):							#if the motor setting is zero (full stop)
            self.motor1_dir.low()				#then set the direction pin LOW
            self.motor1_PWM.duty_u16(0)			#and the speed pin to always be LOW.... with both sides LOW, no current flows through the motor and the motor is off
            
        if (MotorL>0):							#if the motor is supposed to be moving forward
            self.motor1_dir.high()				#set the direction pin HIGH
            self.motor1_PWM.duty_u16(int((65536-Motor_Start)-((MotorL/128)*(65536-Motor_Start)))) #and then figure out how often to set the speed pin LOW. Since the motor runs when the direction pin is HIGH and the speed pin is LOW
                                                                                                    #you increase the speed of the motor by decreasing the duty cycle of the speed pin
        
        if (MotorL<0):							#if the motor is supposed to be moving in reverse
            self.motor1_dir.low()				#set the direction pin LOW
            self.motor1_PWM.duty_u16(int((Motor_Start)-((MotorL/128)*(65536-Motor_Start))))		#and then figure out how often to set the speed pin HIGH. In reverse the motor runs when the dir pin is LOW and the speed pin is HIGH
                                                                                                    #so to increase the speed of the motor you increase the duty cycle of the speed pin
        if (MotorR==0):				#repeat the logic for the Left Motor, but for the Right hand motor
            self.motor2_dir.low()
            self.motor2_PWM.duty_u16(0)
            
        if (MotorR>0):
            self.motor2_dir.high()
            self.motor2_PWM.duty_u16(int((65536-Motor_Start)-((MotorR/128)*(65536-Motor_Start))))
           
        if (MotorR<0):
            self.motor2_dir.low()
            self.motor2_PWM.duty_u16(int((Motor_Start)-((MotorR/128)*(65536-Motor_Start))))
            
    def set_Motor3(self,Motor3):
        
        print("Applying Power to Motor3:",Motor3)		# because they are the motor speed values on a scale of -128(reverse) to +128(forward). Zero is "stop". Motor3 and Motor4 are for future expansion if needed.
        Motor_Start=25000	#Each motor/gearbox combo has a bit of drag. This is the pwm threshold where the motors actually get enough power to overcome inertia and begin to turn. Default is 25000, but feel free to tweak this.
                            #In the Arduino IDE, the analogWrite function allows PWM values from 0-255 because it is 8 bit resolution, but PWM on the PicoW has 16 bit resolution, so the range of values is 0-65,535.
                            #so a Motor_Start value means that when you start out, the motor immediately jumps to about 40% of "full speed" (25K/65K=40%). Anything less might not move because of the drag of the gearbox and motor bearings.
        
        Motor3=Motor3*1		#if motor turns backwards, set this to -1... or change how you have your motors plugged in!
        
        if (Motor3==0):				#repeat the logic from the Drive Motors, but for Motor3
            self.motor3_dir.low()
            self.motor3_PWM.duty_u16(0)
            
        if (Motor3>0):
            self.motor3_dir.high()
            self.motor3_PWM.duty_u16(int((65536-Motor_Start)-((Motor3/128)*(65536-Motor_Start))))
           
        if (Motor3<0):
            self.motor3_dir.low()
            self.motor3_PWM.duty_u16(int((Motor_Start)-((Motor3/128)*(65536-Motor_Start))))

    def set_Servo1(self,angle):		#angle 0 is neutral position +128 is max position -128 is minimum position. Using +/-128 rather than +/-90 degress for comatibility with sliders and joysticks in the html file
            if(angle>128):
                angle=128
            if(angle<-128):
                angle=-128
            max_position=2000		#pulse length in us to achieve maximum servo angle of +90 degrees
            min_position=1000		#you can tweak these values to maximize your servo operation
            pulse_us=int((min_position+((max_position-min_position)/256)*(angle+128)))
            self.servo1.duty_ns(1000*pulse_us)
            print("Setting Servo1 to:",pulse_us," uS")
    