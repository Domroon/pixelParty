# Include the board's default manifest
include("$(PORT_DIR)/boards/manifest.py")

# add my modules that should be freezed in firmware
module("networking.py")
module("i2c_lcd.py") # find another one - no licens
module("lcd_api.py") # find another one - no license
module("ulogging.py")