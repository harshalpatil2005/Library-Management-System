# config.py

DATABASE_HOST = "localhost"
DATABASE_USER = "root"
DATABASE_PASSWORD = "your_mysql_password"  # Set your real password in config_local.py
DATABASE_NAME = "library_management"


# UI Colors
PRIMARY_COLOR = '#4a90e2'   # A clean blue for buttons and highlights
SECONDARY_COLOR = '#32a852' # A complementary green for success messages
ACCENT_COLOR = '#d9534f'    # A red for danger/error messages
BACKGROUND_COLOR = '#f0f0f0' # A light gray for window backgrounds
TEXT_COLOR = '#333333'      # Dark gray for text
BUTTON_COLOR = '#ffffff'    # White for button text

# Load private overrides (not uploaded to GitHub)
try:
    from config_local import *
except ImportError:
    pass