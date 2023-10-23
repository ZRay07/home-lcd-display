from src.core.lcd_interface import LCD_Interface
from datetime import datetime, timedelta
from time import sleep

class Dinner(LCD_Interface):
    """
    A class to display planned dinners.
    """
    def __init__(self, verbosity):
        super().__init__(verbosity)

    def get_main_course(self, json_data, date, day_of_week):
        """
        Fetches the main course from a nested JSON data structure based on the given date and day of the week.
        
        Parameters:
        - json_data (dict): The JSON data containing the menu in nested dictionaries.
        - date (str): The date (formatted as MM/DD) for which the main course is to be fetched.
        - day_of_week (str): The day of the week (all lowercase) for which the main course is to be fetched.
        
        Returns:
        str: The main course as a string if the date and day of the week are found, otherwise returns "Data not found for the given date and day of the week."
        
        Example:
        >>> get_main_course({
        ...     "10/16": {
        ...         "wednesday": {
        ...             "main": "broccoli alfredo",
        ...             "side 1": "None",
        ...             "side 2": "None",
        ...             "side 3": "None"
        ...         }
        ...     }
        ... }, "10/16", "wednesday")
        'broccoli alfredo'
        """
        try:
            # Access the date key in the JSON data
            date_data = json_data[date]
            
            # Access the day of the week key in the date_data
            day_data = date_data[day_of_week]
            
            # Fetch and return the main course
            return day_data['main']
            
        except KeyError:
            # Handle cases where the date or day_of_week is not found
            return "Data not found for the given date and day of the week."
        
    def get_sides(self, json_data, date, day_of_week):
        """
        Fetches the side dishes from a nested JSON data structure based on the given date and day of the week.
        
        Parameters:
        - json_data (dict): The JSON data containing the menu in nested dictionaries.
        - date (str): The date (formatted as MM/DD) for which the sides are to be fetched.
        - day_of_week (str): The day of the week (all lowercase) for which the sides are to be fetched.
        
        Returns:
        list: A list of side dishes as strings. If a side is 'None', it is replaced with an empty string.
        
        Example:
        >>> get_sides({
        ...     "10/16": {
        ...         "tuesday": {
        ...             "main": "chicken",
        ...             "side 1": "rice",
        ...             "side 2": "pepper",
        ...             "side 3": "None"
        ...         }
        ...     }
        ... }, "10/16", "tuesday")
        ['rice', 'pepper', '']
        """
        try:
            # Access the date key in the JSON data
            date_data = json_data[date]
            
            # Access the day of the week key in the date_data
            day_data = date_data[day_of_week]
            
            # Fetch the sides and replace 'None' with an empty string
            sides = [day_data[f'side {i+1}'] for i in range(3) if day_data[f'side {i+1}'] != 'None']
            
            return sides
        
        except KeyError:
            # Handle cases where the date or day_of_week is not found
            return "Data not found for the given date and day of the week."
        
    def main_course_display(self, main_course):
        """
        Displays the main course to the first line of the LCD display.

        If the main course is less than or equal to 16 characters, it will
        use the `write_centered` function to write the main course to the LCD
        display and center the string. If the main course is longer than 16
        characters, it uses the `scroll_text` function to display the information.
        """
        main_str = f"Main: {main_course}"
        if len(main_str) <= 16:
            self.write_centered(0, main_str)
        else:
            self.scroll_text(main_str, 0, 0.5)

    def sides_display(self, sides):
        """
        Displays the sides to the second line of the LCD display.

        Sides are stored as a list. If there are no sides, the list is stored
        as empty strings. 
        
        If the list is only empty strings, then "No sides" is printed.
        
        If there is only one side, then "Side: {side 1}" is printed.

        If there is multiple sides, they will be concatenated in the form:
        "Sides: {side 1} + {side 2} + {side 3}". The " + {side 3}" is only
        included if it exists in the list.

        If the full string is less than or equal to 16 characters, the 
        `write_centered` function will be used to print the string to the LCD display.

        If the full string is longer than 16 characters, the `scroll_text`
        function will be used to print the string to the LCD display.

        Parameters:
            - sides (list):
                The list of sides to be printed to the LCD display.
        """
        # Check if the list is empty
        if len(sides) == 0:
            self.write_centered(1, "No sides")
            return

        # Check if there is only one side
        if len(sides) == 1:
            sides_str = f"Side: {sides[0]}"

        elif len(sides) > 1:
            # For multiple sides, start building the string
            sides_str = "Sides: "

            # Add sides to the string
            for i, side in enumerate(sides):
                sides_str += side
                if i < len(sides) - 1:
                    sides_str += " + "

        else:
            return "Invalid list of sides"

        # Check the length of the final string and display accordingly
        if len(sides_str) <= 16:
            self.write_centered(1, sides_str)
        else:
            self.scroll_text(sides_str, 1, 0.5)

    def get_weekday_and_monday_date(self):
        """
        Gets the date of the current week's monday.

        Dinner plans are stored by week and by day of the week. The week is
        stored as MM/DD of that weeks monday. So the week of October 23-30
        would be saved under the 10/23 structure. Below this week structure,
        dinner plans are split by days of the week (lowercase e.g. monday, 
        tuesday, sunday, etc.)

        Returns:
            - str: the date of the current week's monday in MM/DD format
            - str: the current weekday
        """
        # Get the current date
        current_date = datetime.now().date()

        # Get the current weekday (0=monday, 1=tuesday, 2=wednesday, etc.)
        current_weekday = current_date.weekday()

        # Calculate the date for Monday of the current week
        monday_date = current_date - timedelta(days=current_weekday)

        # Get the month and day
        month = monday_date.month
        day = monday_date.day

        # Get into MM/DD format
        monday_date_str = f"{month}/{day}"

        # Dict to store mapping from int to string weekday
        weekdays = {
            0: "monday",
            1: "tuesday",
            2: "wednesday",
            3: "thursday",
            4: "friday",
            5: "saturday",
            6: "sunday"
        }
        # Convert int to string using dict key-value pair
        current_weekday_str = weekdays.get(current_weekday)

        return monday_date_str, current_weekday_str

    def dinner_plan_display(self):
        """
        Fetches the dinner plan of the day and prints it to LCD display.
        """
        # Load json data
        dinner_data = self.load_data('dinner_data.json')
        
        # Get the date of the current week's monday and the current day
        monday_date, current_weekday = self.get_weekday_and_monday_date()

        # Load the main course and sides for the current day
        main_course = self.get_main_course(dinner_data, monday_date, current_weekday)
        sides = self.get_sides(dinner_data, monday_date, current_weekday)

        # Display data to LCD
        self.main_course_display(main_course)
        self.sides_display(sides)
        

if __name__ == "__main__":
    dinner_view = Dinner(1)
    dinner_view.dinner_plan_display()

