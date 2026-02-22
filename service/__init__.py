"""
Package: service
Package for the application models and service routes
This module creates and configures the Flask app and sets up the logging
and SQL database
"""
import sys
from flask import Flask
from flask_talisman import Talisman   # ← NEW: security headers
from flask_cors import CORS           # ← NEW: CORS policies
from service import config
from service.common import log_handlers

# Create Flask application
app = Flask(__name__)
app.config.from_object(config)

# ── Security ──────────────────────────────────────────────────────────────────
# Flask-Talisman: adds secure HTTP headers to every response.
# Talisman will also redirect plain-HTTP requests to HTTPS by default;
# tests override that behaviour by setting talisman.force_https = False.
talisman = Talisman(app)   # ← NEW

# Flask-Cors: adds Access-Control-Allow-Origin: * to every response,
# which lets browsers make cross-origin requests to this API.
CORS(app)                  # ← NEW
# ─────────────────────────────────────────────────────────────────────────────

# Import the routes After the Flask app is created
# pylint: disable=wrong-import-position, cyclic-import, wrong-import-order
from service import routes, models  # noqa: F401 E402

# pylint: disable=wrong-import-position
from service.common import error_handlers, cli_commands  # noqa: F401 E402

# Set up logging for production
log_handlers.init_logging(app, "gunicorn.error")

app.logger.info(70 * "*")
app.logger.info("  A C C O U N T   S E R V I C E   R U N N I N G  ".center(70, "*"))
app.logger.info(70 * "*")

try:
    models.init_db(app)  # make our database tables
except Exception as error:  # pylint: disable=broad-except
    app.logger.critical("%s: Cannot continue", error)
    # gunicorn requires exit code 4 to stop spawning workers when they die
    sys.exit(4)

app.logger.info("Service initialized!")
