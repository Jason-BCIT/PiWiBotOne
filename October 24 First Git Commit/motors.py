from machine import Pin, PWM
from time import sleep

motor1_dir=machine.Pin(12, mode=Pin.OUT)
motor1_PWM=PWM(machine.Pin(13))
motor1_PWM.freq(5000)
motor1_PWM.duty_u16(00000)


motor2_dir=machine.Pin(14, mode=Pin.OUT)
motor2_PWM=PWM(machine.Pin(15))
motor2_PWM.freq(5000)
motor2_PWM.duty_u16(00000)
