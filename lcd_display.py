from datetime import datetime
from time import sleep

from RPLCD.i2c import CharLCD


class LCD():
    def __init__(self):
        self.lcd = CharLCD(i2c_expander="PCF8574", address=0x27, port=1, cols=16, rows=2, dotsize=8, charmap='A02',
              auto_linebreaks=True)
        self.lcd.clear()

    def format_for_lcd(input_string):
        # Ensure the input string is no more than 32 characters
        truncated_string = input_string[:32]

        # If the string is 16 characters or less, it fits on the first line
        if len(truncated_string) <= 16:
            return truncated_string.ljust(16)  # Fill with spaces to make 16 characters
        # If the string is between 17 and 32 characters, split it into two lines
        else:
            line1 = truncated_string[:16]
            line2 = truncated_string[16:].ljust(16)  # Fill with spaces if less than 16 characters on the second line
            return f"{line1}\n{line2}"
        
    def print_to_lcd(self, str):
        self.lcd.write_string(str)


class DateTime(LCD):
    def __init__(self):
        super().__init__()
        self.date, self.time = self.get_date_time()

    def get_date_time(self):
        """
        Gets the current date and time using Python std lib datetime.

        Returns:
        str: The formatted date.
        str: The formatted time.
        """
        current_datetime = datetime.now()
        date = current_datetime.strftime('%B %d, %Y')
        time = current_datetime.strftime('%I:%M:%S %p')

        def format_date(date):
            """
            Format a date to be in: 'MMM. DD, YYYY' format.

            Parameters:
            - date (str): The date in 'Month Day, Year' format.

            Returns:
            str: The formatted date.
            """

            def find_day_index(str):                    # Find where DAY starts e.g. October ->1...<-
                for ind, char in enumerate(str):
                    if char.isdigit():
                        return ind
                return None
            
            def remove_characters(str, start, end):     # Keep only first 3 letters of month e.g. Oct, Nov, Jan...
                return str[:start] + " " + str[end:] + "    "
            
            formatted_date = remove_characters(date, 3, find_day_index(date))       
            return formatted_date

        date = format_date(date)
        return date, time
    


    


    







def main():
    date_time_view = DateTime()
    date_time_view.print_to_lcd(date_time_view.date)
    date_time_view.print_to_lcd(date_time_view.time)

if __name__ == "__main__":
    main()