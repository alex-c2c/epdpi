from typing import Any
from gpiozero import Button

class MyButton:
    btn: Button
    state: int
    pin: int
    callback: Any
    
    def __init__(self, pin, callback):
        self.btn = Button(pin, bounce_time=0.05, hold_repeat=False)
        self.state = 0
        self.pin = pin
        self.callback = callback
        
        self.btn.when_pressed = self.when_pressed
        self.btn.when_released = self.when_released
    
    def when_pressed(self):
        print("press")
        if self.state != 0:
            return
        
        self.state = 1
    
    def when_released(self):
        print("release")
        if self.state != 1:
            return
    
        self.state = 0
        self.callback()
        
        
        