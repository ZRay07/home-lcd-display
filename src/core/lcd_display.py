from RPLCD.i2c import CharLCD
from time import sleep

class HomeDashboard(CharLCD):
    """
    A class to interface with a 16*2 LCD display

    Parameters
        - verbosity (int):
            Changes how much information is displayed. Can be 0 or 1 or 2.
            Default: 1
    """

    def __init__(self, verbosity=1):
        super().__init__(i2c_expander="PCF8574",
                           address=0x27,
                           port=1, 
                           cols=16,
                           rows=2, 
                           dotsize=8)
        self.clear()

        if verbosity == 0 or verbosity == 1 or verbosity == 2:
            print(f"verbosity: {verbosity}")
            self.verbosity = verbosity
        else:
            raise ValueError(
                'The ``verbosity`` argument must be either ``0`` or ``1`` or ``2``')  
        
    def set_verbosity(self, verbosity):
        self.verbosity = verbosity
    
    def write_centered(self, line, msg):
        """
        Write a string to the center of a line on the LCD display.

        This function expects an input string smaller than 16 characters. It
        centers the string on the LCD display by subtracting the length of the
        string from 16, and dividing the remaining cells by 2. This value is
        the starting cell. If the string len is an odd number, it will be off
        center by 1 cell.

        Parameters
            - line (int):
                line to print to on LCD display (0 or 1)
                Default: 0 (line 1)
            - msg (str):
                the string to display

        Raises
            - ValueError: if the str is too long or the line num is incorrect
        """
        if len(msg) <= 16:
            # LCD is 16 cells long. To center a message, subtract message length from
            # 16 and divide the remaining cells by 2 to get the starting position.
            start_pos = (16 - len(msg)) / 2
            start_pos = int(start_pos)
        else:
            raise ValueError(
                'The ``msg`` argument must be no longer than 16 characters')
        
        if line == 0:
            self.cursor_pos = (0, start_pos)
            self.write_string(msg)
        elif line == 1:
            self.cursor_pos = (1, start_pos)
            self.write_string(msg)
        else:
            raise ValueError(
                'The ``line`` argument must be either ``0`` or ``1``')
        
    def scroll_text(self, text, line, delay):
        """
        Scrolls the given text from left to right on the specified line of a 16x2 LCD display.

        Parameters:
            - text (str): The text to be scrolled.
            - line (int): The line number on which to scroll the text (0 for the first line, 1 for the second line).
            - delay (float): The delay in seconds between each step of scrolling.

        Raises:
            ValueError: If the line number is not 0 or 1.
        """
        if line not in [0, 1]:
            raise ValueError('Line number must be 0 or 1')
        
        text = ' ' * 16 + text + ' ' * 16  # Padding text with spaces
        for i in range(len(text) - 15):
            display_text = text[i:i + 16]
            self.cursor_pos = (line, 0)
            self.write_string(display_text)
            sleep(delay)

def main():
    home_dashboard = HomeDashboard()
    long_str = "This is a long string to display scrolling text functionality"
    home_dashboard.scroll_text(long_str, 1, 0.5)
    home_dashboard.scroll_text(long_str, "Hello", 1)

if __name__ == "__main__":
    main()