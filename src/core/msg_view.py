from src.core.lcd_interface import LCD_Interface


class Message(LCD_Interface):
    """
    A class to display messages uploaded over a web page.
    """
    def __init__(self, verbosity):
        super().__init__(verbosity)
    