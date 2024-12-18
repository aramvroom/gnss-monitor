from math import pi
SLEEP_TIME_FACTOR = 2  # How much the sleep time increases with each failed attempt
MAX_RECONNECTS = 1
MAX_RECONNECT_TIMEOUT = 1200
NTRIP_INTERVAL = 1  # So the first one is 1 second
PROPAGATION_INTERVAL = 1
PLOTTING_INTERVAL = 0.1

# Natural & WGS84 Constants
MU_EARTH = 3.986004418e14
ROT_RATE_EARTH = 7292115.0e-11
SEC_IN_HOUR = 3600
HOURS_IN_DAY = 24
DAYS_IN_WEEK  = 7
SEC_IN_WEEK = DAYS_IN_WEEK * HOURS_IN_DAY * SEC_IN_HOUR
SPEED_OF_LIGHT = 2.99792458e8
WGS84_SEMI_MAJOR_AXIS = 6378137
WGS84_FIRST_ECCENTRICITY_SQUARED = 6.69437999014e-3
RAD_TO_DEG = 180 / pi
DEG_TO_RAD = pi / 180

DF_GALILEO_EPH = 1046
MAX_SATS = 36
GPS_WEEKS_ROLLOVER = 1024