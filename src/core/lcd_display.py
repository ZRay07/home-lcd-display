from RPLCD.i2c import CharLCD

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
        Write a string to the center of the LCD display.

        Parameters
            - line (int):
                line to print to on LCD display (0 or 1)
                Default: 0 (line 1)
            - msg (str):
                the string to display
        """

        # LCD is 16 cells long. To center a message, subtract message length from
        # 16 and divide the remaining cells by 2 to get the starting position.
        start_pos = (16 - len(msg)) / 2
        start_pos = int(start_pos)
        
        if line == 0:
            self.cursor_pos = (0, start_pos)
            self.write_string(msg)

        elif line == 1:
            self.cursor_pos = (1, start_pos)
            self.write_string(msg)

        else:
            raise ValueError(
                'The ``line`` argument must be either ``0`` or ``1``')    

def main():
    home_dashboard = HomeDashboard()
    home_dashboard.write_string("Test")

if __name__ == "__main__":
    main()