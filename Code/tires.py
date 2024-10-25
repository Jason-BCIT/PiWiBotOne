from machine import Pin, PWM

class Tires():
    def __init__(self):
        self.motor1_dir=Pin(12, mode=Pin.OUT)
        self.motor1_PWM=PWM(Pin(13))
        self.motor1_PWM.freq(5000)
        self.motor1_PWM.duty_u16(00000)

        self.motor2_dir=Pin(14, mode=Pin.OUT)
        self.motor2_PWM=PWM(Pin(15))
        self.motor2_PWM.freq(5000)
        self.motor2_PWM.duty_u16(00000)



    def apply_power(self, MotorL, MotorR, Motor3, Motor4):
        print("Applying Power ",MotorL," ",MotorR," ",Motor3," ",Motor4)
        Motor_Start=25000	#the pwm threshold where the motors actually get enough power to overcome inertia and begin to turn
        
        MotorL=MotorL*1		#if motor turns backwards, set this to -1
        MotorR=MotorR*-1		#if motor turns backwards, set this to 1
        
        if (MotorL==0):
            self.motor1_dir.low()
            self.motor1_PWM.duty_u16(0)
            
        if (MotorL>0):
            self.motor1_dir.high()
            self.motor1_PWM.duty_u16(int((65536-Motor_Start)-((MotorL/128)*(65536-Motor_Start))))
        
        if (MotorL<0):
            self.motor1_dir.low()
            self.motor1_PWM.duty_u16(int((Motor_Start)-((MotorL/128)*(65536-Motor_Start))))
            
        if (MotorR==0):
            self.motor2_dir.low()
            self.motor2_PWM.duty_u16(0)
            
        if (MotorR>0):
            self.motor2_dir.high()
            self.motor2_PWM.duty_u16(int((65536-Motor_Start)-((MotorR/128)*(65536-Motor_Start))))
            print("MotorR=",(int((65536-Motor_Start)-((MotorR/128)*(65536-Motor_Start)))))
        
        if (MotorR<0):
            self.motor2_dir.low()
            self.motor2_PWM.duty_u16(int((Motor_Start)-((MotorR/128)*(65536-Motor_Start))))
            print("MotorR=",(int((Motor_Start)-((MotorR/128)*(65536-Motor_Start)))))
            
        
