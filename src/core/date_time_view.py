from src.core.lcd_interface import LCD_Interface
from datetime import datetime
from time import sleep

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
            - date (str): The date.
            - time (str): The formatted time.
        """
        current_datetime = datetime.now()
        date = current_datetime.strftime('%B %d, %Y')
        time = current_datetime.strftime('%I:%M:%S %p')
        return date, time
        

    def format_date(self, date):
        """
        Format a date to be in: 'MMM. DD, YYYY' format.

        Parameters:
            - date (str): The date in 'Month Day, Year' format.

        Returns:
            formatted_date (str): The formatted date.
        """
        def find_day_index(date):                    # Find where DAY starts e.g. October ->1...<-
            for ind, char in enumerate(date):
                if char.isdigit():
                    return ind
            return None
        
        def remove_characters(date, start, end):     # Keep only first 3 letters of month e.g. Oct, Nov, Jan...
            return date[:start] + " " + date[end:]
        
        formatted_date = remove_characters(date, 3, find_day_index(date))    

        return formatted_date
    
    def poll_date_time(self):
        while True:
            try:
                self.date, self.time = self.get_date_time()
                self.date = self.format_date(self.date)
                self.write_centered(0, self.date)
                self.write_centered(1, self.time)
                sleep(1)

            except KeyboardInterrupt:
                print("\nExiting...")
                return
            


def main():
    date_time_view = DateTime(1)
    date_time_view.poll_date_time()

if __name__ == "__main__":
    main()