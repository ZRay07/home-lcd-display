import asyncio
from time import sleep

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
        self.main_button = 0
        self.secondary_button = 0
        self.refresh_LCD = True

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
        
        Pauses the refresh of the LCD display. Clears the LCD display. Changes
        the "view" of the LCD display. Continues to refresh the LCD display.
        """
        # Pause the refresh of the LCD display
        self.refresh_LCD = None

        # Clear the LCD display
        self.lcd_interface.clear()

        # If main button is pressed -> cycle to next view
        if channel == self.INP_PIN_MAP["main_btn"]:
            # Set secondary button back to 0 so that it's always on default view
            self.secondary_button = 0

            # Main btn count goes from 0 to 1 to 2 to 3 and then back to 0 (4 views)
            if self.main_button < 3:
                self.main_button += 1
            else:
                self.main_button = 0

            print(f"self.main_button: {self.main_button}")
        
        # If secondary button is pressed -> switch to alt screen of same view
        elif channel == self.INP_PIN_MAP["secondary_btn"]:

            # Scndry btn count goes from 0 to 1 and then back to 0 (only one alt screen / view)
            if self.secondary_button < 1:
                self.secondary_button += 1
            else:
                self.secondary_button = 0

            print(f"self.secondary_button: {self.secondary_button}")

        # Reset the flag so the display can continue to refresh
        self.refresh_LCD = True

    def cycle_views(self):
        """
        This function cycles through the 4 views.

        4 "views" exist in the project (date/time, weather, dinner, and msg board).
        The user can cycle to the next "view" by using the main button on the
        breadboard. Inside of a "view", the user can press the secondary button
        to show additional information.
        """
        while self.refresh_LCD is not None:
            try:
                if self.main_button == 0:
                    if self.secondary_button == 0:
                        self.lcd_interface.write_centered(0, "date/time view")
                    elif self.secondary_button == 1:
                        self.lcd_interface.write_centered(0, "alt view")

                elif self.main_button == 1:
                    if self.secondary_button == 0:
                        self.lcd_interface.write_centered(0, "current weather")
                    elif self.secondary_button == 1:
                        self.lcd_interface.write_centered(0, "forecast")

                elif self.main_button == 2:
                    if self.secondary_button == 0:
                        self.lcd_interface.write_centered(0, "dinner view")
                    elif self.secondary_button == 1:
                        self.lcd_interface.write_centered(0, "tmr dinner")

                elif self.main_button == 3:
                    if self.secondary_button == 0:
                        self.lcd_interface.write_centered(0, "msg board")
                    elif self.secondary_button == 1:
                        self.lcd_interface.write_centered(0, "alt board")

                sleep(1)

            except KeyboardInterrupt:
                print("\nExiting...")
                return
        

if __name__ == "__main__":
    home_dashboard = HomeDashboard()
    home_dashboard.cycle_views()