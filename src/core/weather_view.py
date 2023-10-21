import aiohttp
import asyncio
from datetime import datetime, timedelta
import requests
from time import sleep

from src.core.lcd_interface import LCD_Interface


class Weather(LCD_Interface):
    """
    A class to display the weather view.

    To avoid waiting for the API request every time the script is run,
        recent weather data will be stored in a file. Each time the script
        runs, it can load the data from this file. Meanwhile, an API request
        can be initiated to update the file with the latest data.
    """
    def __init__(self, verbosity):
        super().__init__(verbosity)
        self.api_key="aefa40f03e984c69afa184404230610"
        self.location="43.95877170902545, -70.01448164545899"
        self.current_weather_url = f"http://api.weatherapi.com/v1/current.json?key={self.api_key}&q={self.location}"
        self.forecast_url = f"http://api.weatherapi.com/v1/forecast.json?key={self.api_key}&q={self.location}&days=2"
        self.current_weather = None
        self.forecast = None
        self.update_task = None
        self.time_passed = 0
        self.degree_symbol = (
            0b00000,
            0b00100,
            0b01010,
            0b00100,
            0b00000,
            0b00000,
            0b00000,
            0b00000
        )
        self.create_char(0, self.degree_symbol)

    def get_current_weather(self):
        """
        Gets current weather information using WeatherAPI.

        Returns:
            - current_weather (json): 
                response from the WeatherAPI in json string format.
        """
        # Fetch current weather data
        current_response = requests.get(self.current_weather_url)
        current_weather = current_response.json()
        current_weather = self.add_timestamp(current_weather)
        return current_weather

    def get_forecast(self):
        """
        Gets future weather information using WeatherAPI.

        Returns:
            - forecast (json):
                response from the WeatherAPI in json string format.
        """
        # Fetch forecast data
        forecast_response = requests.get(self.forecast_url)
        forecast = forecast_response.json()
        forecast = self.add_timestamp(forecast)
        return forecast
        
    def print_last_updated(self):
        """
        Prints last recorded Weather data timestamp to the LCD display.

        Weather information is stored in 'weather_data.json' file. Along with
        the data, there is a date/time stamp. This date/time stamp stores the
        time at which the 'feels like temperature' and 'condition' were
        measured. When the weather loop starts, it loads previous data,
        therefore, printing the last update time shows the user when the last
        weather information data is coming from.
        """
        # Load existing data from json file to print time it was updated
        loaded_weather = self.load_data('weather_data.json')
        loaded_time = loaded_weather['current']['last_updated']
        formatted_loaded_time = loaded_time[11:]
        int_hour = int(formatted_loaded_time[:2])
        
        # Reformat the time into standard time (as opposed to military)
        if int_hour >= 12:
            int_hour = int_hour - 12
            str_hour = f"0{str(int_hour)}"
            formatted_loaded_time = f"{str_hour}:{formatted_loaded_time[3:]} PM"

        else:
            formatted_loaded_time = f"{loaded_time[11:]} AM"

        self.write_centered(0, "Last Updated")
        sleep(2)
        self.clear()
        self.write_centered(0, loaded_time[:10])
        self.write_centered(1, formatted_loaded_time)
        sleep(7)
        self.clear()
        
    async def fetch_and_update(self, api_url):
        """
        Asynchronously sends a GET request to the specified API URL, retrieves the JSON response,
        and saves the data to a file.

        The function initiates an asynchronous HTTP session, sends a GET request to the provided
        API URL, awaits the JSON response, and calls save_data function to save the response data
        to a file named 'weather_data.json'.

        Parameters:
            - api_url (str): 
                The URL of the API endpoint to send the GET request to.

        Raises:
            - aiohttp.ClientError: If an HTTP error occurs.
            - aiohttp.ClientResponseError: If the HTTP request returns a status other than 2xx.
            - aiohttp.ContentTypeError: If the response body is not JSON.
            - json.JSONDecodeError: If there's an error decoding the JSON response.
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                data = await response.json()
                if api_url == self.current_weather_url:
                    self.current_weather = self.load_data('weather_data.json')
                self.save_data(data, 'weather_data.json')
                return data

    def start_update_task(self, api_url):
        self.update_task = asyncio.create_task(self.fetch_and_update(api_url))

    async def current_weather_display(self):
        """
        Displays current weather information to LCD display.

        If the new request has not completed, it will display previous
        information stored in the weather_data.json file. Once the request
        has completed, it will update the display to show more current info.
        """
        # Start the update task
        self.start_update_task(self.current_weather_url)

        self.print_last_updated()

        while True:
            try:
                if self.update_task.done():
                    print("new weather information...")
                    self.print_last_updated()
                    self.current_weather = self.update_task.result()

                    # weather data is updated roughly every 15 mins (900 sec)
                    if self.time_passed >= 900:
                        # Restart the update task
                        self.start_update_task(self.current_weather_url)

                if self.current_weather is not None:
                    # Extracting current day weather information
                    current_temperature = self.current_weather['current']['temp_f']
                    str_current_temp = f"{current_temperature}°F"
                    current_condition = self.current_weather['current']['condition']['text']
                    # Output the data to LCD
                    self.write_centered(0, str_current_temp)
                    self.cursor_pos = (0, 9)
                    self.write_string('\x00')
                    self.write_centered(1, current_condition)

                    # Reset current_weather flag
                    self.current_weather = None

                else:
                    # Load existing data from json file and extract same info
                    loaded_weather = self.load_data('weather_data.json')
                    loaded_temp = loaded_weather['current']['temp_f']
                    str_loaded_temp = f"{loaded_temp}°F" 
                    loaded_condition = loaded_weather['current']['condition']['text']
                    # Output the data to LCD
                    self.write_centered(0, str_loaded_temp)
                    self.cursor_pos = (0, 9)
                    self.write_string('\x00')
                    self.write_centered(1, loaded_condition)

                await asyncio.sleep(60)
                self.time_passed = self.time_passed + 60

            except KeyboardInterrupt:
                print("\nExiting...")
                return

    def forecast_display(self):
        """
        Displays weather forecast of the next day.

        This function first checks 'forecast_data.json' for the last time the
        forecast data was fetched from the API. If the current time is over 1
        hour difference from the last fetch, it makes a new API request for
        updated data.

        Then, this data is displayed to the LCD display.

        Parameters
            - 

        Returns:
            - 
        """
        # Compare previous fetch time to current time
        old_forecast_data = self.load_data("forecast_data.json")
        last_fetched_str = old_forecast_data["last_fetched"]
        last_fetched_time = datetime.fromisoformat(last_fetched_str)

        current_time = datetime.now()

        time_difference = current_time - last_fetched_time

        if time_difference >= timedelta(hours=1):
            self.write_centered(0, "Fetching new")
            self.write_centered(1, "weather data")
            self.forecast_data = self.get_forecast()
            self.save_data(self.forecast_data, "forecast_data.json")
            
            # Once the new data has been stored, clear the LCD display
            self.clear()

        # Extracting tomorrow's weather information
        self.forecast_data = self.load_data("forecast_data.json")
        tomorrow_temperature = self.forecast_data['forecast']['forecastday'][1]['day']['avgtemp_f']
        str_tomorrow_temp = f"{tomorrow_temperature}°F"
        tomorrow_condition = self.forecast_data['forecast']['forecastday'][1]['day']['condition']['text']

        if len(tomorrow_condition) >= 16:
            tomorrow_condition = tomorrow_condition[:16]

        # Output the data to the LCD display
        print(f"Tomorrow's temperature: {tomorrow_temperature}°F")
        print(f"Tomorrow's condition: {tomorrow_condition}")

        self.write_centered(0, str_tomorrow_temp)
        self.cursor_pos = (0, 9)
        self.write_string('\x00')
        self.write_centered(1, tomorrow_condition)




def main():
    weather_view = Weather(1)
    #asyncio.run(weather_view.current_weather_display())
    weather_view.forecast_display()

if __name__ == "__main__":
    main()