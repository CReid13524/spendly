"""App entry point."""
from FlaskApp import create_app

app, api = create_app()

if __name__ == "__main__":
    # Only for local development
    app.run(host="0.0.0.0", port=5000, debug=True)