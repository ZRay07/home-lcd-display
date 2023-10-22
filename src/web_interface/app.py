from pathlib import Path

from flask import Flask, request, render_template_string, redirect, url_for


# Define the current file's path
current_path = Path(__file__)

# Initializing the Flask application
app = Flask(__name__)

# Define a route for submitting the form, accepting POST requests
@app.route('/submit', methods=['POST'])
# Function to handle form submission
def submit():
    # Get the submitted message from the form
    message = request.form['message']
    # TODO: send message to LCD

    # Redirect back to the home page (where index.html is served)
    return redirect(url_for('home'))

# Route for the home page
@app.route('/')
# Function to serve the HTML form
def home():
    # Render the HTML form from a string (assuming it is read from "index.html")
    return render_template_string(open(current_path.parent / "index.html").read())

# main entry point of the application
if __name__ == "__main__":
    # Run the application on all available network interfaces
    # and on port 80 (HTTP)
    app.run(host="0.0.0.0")#, port=80)


