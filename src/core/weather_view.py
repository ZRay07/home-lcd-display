import configparser
from datetime import datetime, timedelta
import requests
from threading import Thread, Lock
from time import sleep

from src.core.lcd_interface import LCD_Interface


class Weather(LCD_Interface):
    """
    A class to fetch weather data and display the weather view.

    New data is fetched from the Open Meteo API every 10 minutes in a seperate
    thread. This data is stored inside of weather_data.json file in the
    src/data directory. The data consists of temperature and weather codes
    for current day and tomorrow. Weather codes are two digit integers which
    translate to a condition (e.g., sun/clear skies, rain, snow, etc.).

    There exists two functions for displaying data to the LCD display. One
    function displays current temperature and current condition. The other
    function displays the max temperature forecasted for tomorrow and the
    forecasted condition for tomorrow.
    """
    def __init__(self, verbosity):
        super().__init__(verbosity)
        # Create a Pathlib Path for the JSON file containing weather data
        self.weather_filepath = self.data_directory / 'weather_data.json'
        # Extract the users location from the config file
        self.get_user_location()

        # Initialize a threading lock for safely reading/writing to/from file
        self.weather_lock = Lock()

        # Start the background thread to fetch weather data
        # Daemon threads are good for background processes and do not need
        # to finish execution before exiting the program
        self.weather_thread = Thread(target=self.background_fetch, daemon=True)
        self.weather_thread.start()

    def background_fetch(self):
        """Fetch weather data in the background every 10 minutes."""
        while True:
            self.fetch_weather()
            sleep(600) # Sleep for 10 minutes

    def get_user_location(self):
        """Access the config file for latitude and longitude values"""
        config = configparser.ConfigParser()
        config.read(self.current_path.parent / 'config.ini')

        self.latitude = config['DEFAULT']['latitude']
        self.longitude = config['DEFAULT']['longitude']

        print(f"Location: {self.latitude}, {self.longitude}")

    def fetch_weather(self):
        """
        Fetch weather data from the Open Meteo API and store it in a JSON file.

        This method fetches the current weather data based on the latitude and
        longitude specified in the class instance. The fetched data is then
        saved to a JSON file for subsequent access.

        API Details:
        - Base URL: https://api.open-meteo.com/v1/forecast
        - Open Meteo is a free, open-source Weather API that doesn't require an API key.
        - Parameters:
            - latitude: Latitude of the location.
            - longitude: Longitude of the location.
            - current: Data points to fetch for current weather
                (e.g., temperature, weather code).
            - daily: Data points to fetch for forecasted weather
                (e.g., max temperature, weather code)
            - temperature_unit: Desired unit for temperature values.
                (e.g., "fahrenheit")
            - timezone: Timezone for the location. (e.g., "America/New_York")
            - forecast_days: Number of days to forecast. (e.g., "3")

        Raises:
            - requests.RequestException: If there's an issue with the HTTP request 
                (e.g., server error, timeout, etc.).

        Returns:
            None. The fetched data is saved to 'weather_data.json' in the data directory.
        """
        # URL for the API
        weather_url = "https://api.open-meteo.com/v1/forecast"
        # Parameters for the API request
        params = {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "current": "temperature_2m,weathercode",
            "daily": "temperature_2m_max,weathercode",
            "temperature_unit": "fahrenheit",
            "timezone": "America/New_York",
            "forecast_days": "2"
        }
        try:
            # Fetch current weather data
            current_response = requests.get(weather_url, params=params)
            # Following line will raise exception if HTTP request returns error code
            current_response.raise_for_status()

            # Save the data to a json file
            current_weather = current_response.json()
            with self.weather_lock:
                self.save_data(current_weather, self.weather_filepath)

        except requests.RequestException as e:
            # This will handle any type of RequestException
            # like HTTPError, Timeout, TooManyRedirects, etc.)
            print(f"Error fetching weather data: {e}")


    
    def get_current_data(self):
        """
        Gets the current temp and weathercode from weather_data.json file.
        
        Returns:
            - float: the current temperature in fahrenheit
            - int: the current weathercode (condition)

        Raises:
            - ValueError: if the temperature or current weather code is not
                stored as expected or missing
        """
        # Load the json file into a dict
        with self.weather_lock:
            data = self.load_data(self.weather_filepath)

        # Extract the temperature from the nested "current" dictionary
        current_temp = data.get("current", {}).get("temperature_2m", None)

        # Extract the weathercode
        current_wcode = data.get("current", {}).get("weathercode", None)

        if current_temp is None:
            raise ValueError(
                "The JSON file doesn't contain the expected temp format.")
        
        elif current_wcode is None:
            raise ValueError(
                "The JSON file doesn't contain the expected weathercode format.")
        
        return current_temp, current_wcode
    
    def convert_wcode_to_condition(self, weathercode):
        """
        Convert an int WMO code (ww) to a condition (e.g. sun, clouds, rain)

        WMO Weathercodes are designated by the National Oceanic and
        Atmospheric Administration (NOAA). They provide precise condition
        reports and range from 00-99.

        Official Table: https://www.nodc.noaa.gov/archive/arc0021/0002199/1.1/data/0-data/HTML/WMO-CODE/WMO4677.HTM

        Generally:
            - 00-49: No precipitation at time of observation
                - 00-19: No precipitation at time of observation or preceding hour
                - 20-29: Precipitation, fog, ice fog, or thunderstorm during preceding hour
                - 30-39: Duststorm, sandstorm, drifting or blowing snow during preceding hour
                - 40-49: Fog or ice fog during preceding hour
            - 50-99: Precipitation at time of observation
                - 50-59: Drizzle
                - 60-69: Rain
                - 70-79: Snow
                - 80-99: Rain and snow

        At the current time, I have decided to go with a simple table from the
        Open Meteo docs page. (https://open-meteo.com/en/docs)
        """
        wmo_code_map = self.load_data(self.data_directory / "wmo_code.json")
        condition = wmo_code_map.get(weathercode, None)

        if condition is None:
            raise ValueError(
                "The JSON file doesn't contain the weathercode.")
        
        return condition

    def current_weather_display(self):
        """Displays current weather information (e.g., temp., cond.) to LCD."""
        self.clear()
        temp, weathercode = self.get_current_data()
        condition = self.convert_wcode_to_condition(str(weathercode))
        self.write_centered(0, f"{temp} F")
        self.write_centered(1, condition)

        # Write the degree symbol
        self.cursor_pos = (0, 9)
        self.write_string('\x00')

    def get_forecast_data(self):
        """
        Gets the forecasted max temp and weathercode from weather_data.json file.
        
        Returns:
            - float: the forecasted max temperature in fahrenheit
            - int: the forecasted weathercode (condition)

        Raises:
            - ValueError: if the forecasted max temperature or forecasted
                weather code is not stored as expected or missing
        """
        # Load the json file into a dict
        with self.weather_lock:
            data = self.load_data(self.weather_filepath)

        # Extract the temperature array from the nested "daily" dictionary
        forecast_temps = data.get("daily", {}).get("temperature_2m_max", None)
        forecast_temp = forecast_temps[1]

        # Extract the forecasted weathercode array
        forecast_wcodes = data.get("daily", {}).get("weathercode", None)
        forecast_wcode = forecast_wcodes[1]

        if forecast_temp is None:
            raise ValueError(
                "The JSON file doesn't contain the expected temp format.")
        
        elif forecast_wcode is None:
            raise ValueError(
                "The JSON file doesn't contain the expected weathercode format.")
        
        return forecast_temp, forecast_wcode

    def forecast_display(self):
        """Displays forecast weather info(e.g., temp., cond.) to LCD."""
        self.clear()
        temp, weathercode = self.get_forecast_data()
        condition = self.convert_wcode_to_condition(str(weathercode))
        self.write_centered(0, f"{temp} F")
        self.write_centered(1, condition)

        # Write the degree symbol
        self.cursor_pos = (0, 9)
        self.write_string('\x00')



def main():
    weather_view = Weather(1)
    weather_view.current_weather_display()
    weather_view.forecast_display()
    
if __name__ == "__main__":
    main()