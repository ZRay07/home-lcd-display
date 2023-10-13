from src.core.lcd_interface import LCD_Interface
from src.core.weather_view import Weather
from src.core.date_time_view import DateTime

import RPi.GPIO as GPIO


class HomeDashboard():
    def __init__(self):
        self.lcd_interface = LCD_Interface(1)
        self.weather_view = Weather(1)
        self.date_time_view = DateTime(1)
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        self.setup_gpio()

    # Dictionary to hold the mapping of buttons to GPIO pins
    INP_PIN_MAP = {
        "main_btn" : 37,
        "secondary_btn" : 36
    }

    def setup_gpio(self):
        """
        Sets up the GPIO pins used to interface with the buttons. Adds callback
        functions to the two input buttons.
        """
        # Initialize the GPIO pins
        GPIO.setup(list(self.INP_PIN_MAP.values()), GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Attach the ISR to the buttons
        GPIO.add_event_detect(self.INP_PIN_MAP["main_btn"], GPIO.RISING,
                              callback=self.button_pressed_callback, bouncetime=1000)
        GPIO.add_event_detect(self.INP_PIN_MAP["secondary_btn"], GPIO.RISING,
                              callback=self.button_pressed_callback, bouncetime=1000)
        
    def button_pressed_callback(self, channel):
        """
        The function to be called when a button is pressed.
        Changes the "view" of the LCD display
        """
        if channel == self.INP_PIN_MAP["main_btn"]:
            print("main button pressed")
        
        elif channel == self.INP_PIN_MAP["secondary_btn"]:
            print("secondary button pressed")

if __name__ == "__main__":
    home_dashboard = HomeDashboard()