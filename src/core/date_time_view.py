from datetime import datetime
from src.core.lcd_interface import LCD_Interface


class DateTime(LCD_Interface):
    """
    A class to display the current date and time view.

    LCD Line 1: Date (MMM. DD, YYYY)
    LCD Line 2: Time (HH:MM:SS) updated every second.
    """
    def __init__(self, verbosity):
        super().__init__(verbosity)

    def get_date_time(self):
        """
        Gets the current date and time using Python std lib datetime.

        Returns:
            - (str): The formatted date.
            - (str): The formatted time.
        """
        current_datetime = datetime.now()
        date = current_datetime.strftime('%b %d, %Y')
        time = current_datetime.strftime('%I:%M %p')
        return date, time
    
    def date_time_display(self):
        """Get the current date and time and display it to LCD."""
        self.date, self.time = self.get_date_time()
        self.write_centered(0, self.date)
        self.write_centered(1, self.time)

        
def main():
    date_time_view = DateTime(1)
    date_time_view.date_time_display()

if __name__ == "__main__":
    main()