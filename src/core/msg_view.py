from src.core.lcd_interface import LCD_Interface
from src.web_interface.web_interface import WebApp
from time import sleep


class Message(LCD_Interface):
    """
    A class to display messages uploaded over a web page.
    """
    def __init__(self, verbosity):
        super().__init__(verbosity)
        self.web_app = WebApp()
        self.web_app.run()

    def message_display(self):
        """
        Grabs the message from the WebApp class and displays it on LCD.
        """
        while True:
            print("here")
            self.message = self.web_app.message

            self.write_centered(0, self.message)

            sleep(0.5)


if __name__ == "__main__":
    msg_view = Message(1)
    msg_view.message_display()

# TO-DO: Create seperate thread for hosting webpage!!!!!!