from flask import Flask, request, render_template


class WebApp: 
    """
    WebApp encapsulates a Flask application for managing and displaying messages.

    The class is designed to integrate a Flask-based web interface with the
    home dashboard. It allows users to submit messages through a web form,
    stores the last submitted message, and provides an interface to retrieve
    this message for display on an LCD.

    Attributes:
        - app (Flask):
            The Flask application instance.
        - message (str):
            The latest message submitted via the web interface.

    Methods:
        routes(): Registers route handlers for the Flask application.
        get_message(): Retrieves the latest stored message.
        set_message(new_message: str): Updates the stored message.
        display_form(): Route handler for displaying the web form.
        save_text(): Route handler for handling message submission.
        run(): Registers routes and starts the Flask application server.

    See https://flask.palletsprojects.com/en/2.3.x/  for Flask documentation.
    """
    def __init__(self):
        self.app = Flask(__name__)
        self.message = ""

    def run(self):
        """
        Initialize routes for the Flask application and start the application server.

        This method serves two main purposes:
            1. Registers all the routes for the Flask application.
            2. Starts the Flask application server in debug mode.
        """
        self.routes()
        self.app.run(debug=True)

    def routes(self):
        # Define routes
        self.app.add_url_rule("/", "home", self.home)
        self.app.add_url_rule("/submit_msg", "submit_msg", self.submit_msg)
        self.app.add_url_rule("/save_text", "save_text", self.save_text, methods=["POST"])

    def home(self):
        """Render the home page."""
        return render_template("index.html")
    
    def submit_msg(self, message=None):
        """Render the message submission page with an optional message"""
        return render_template("submit_msg.html", message=message)
    
    def save_text(self):
        """Save the text submitted via the form and display a message on submission"""
        self.message = request.form.get("message")
        feedback_message = f"{self.message} received."
        return self.submit_msg(message=feedback_message)


if __name__ == "__main__":
    web_app = WebApp()
    web_app.run()