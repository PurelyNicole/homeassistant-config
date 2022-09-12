# This script is designed to work with ecobee thermostats. It assumes the Comfort Settings are properly set within the Ecobee app.

# Get thermostat to update
thermostat = data.get("thermostat")
weather = data.get("weather")

# Get current home mode and forecasted high temperature for the day.
home_mode = (hass.states.get("input_select.home_mode")).state
current_mode = (hass.states.get(thermostat)).state
today_high = (hass.states.get(weather).attributes['forecast'][0]['temperature'])

# Get current time of day.
if hass.states.is_state("binary_sensor.day", "on"):
  logger.info("Day.")
  time_of_day = "day"
elif hass.states.is_state("binary_sensor.dusk", "on"):
  logger.info("Dusk.")
  time_of_day = "dusk"
elif hass.states.is_state("binary_sensor.night", "on"):
  logger.info("Night.")
  time_of_day = "night"
else:
  logger.warn("No time of day detected.")

# Set thermostat mode based on forecasted high temperature.
if today_high > 80:
  logger.info("Setting mode to cool.")
  operation_mode = "cool"
# Sets heat_cool variables.
elif today_high >= 60 and today_high <= 80:
  logger.info("Setting mode to heat_cool.")
  operation_mode = "heat_cool"
# Sets heat variables.
elif today_high < 60:
  logger.info("Setting mode to heat.")
  operation_mode = "heat"
else:
  logger.warn("Temperature is out of range.")

# Set the operation mode if the thermostat is not already in that mode.
if current_mode != operation_mode:
  logger.info("Set operation mode.")
  hass.services.call("climate", "set_hvac_mode", {"entity_id": thermostat, "hvac_mode": operation_mode}, False)
else:
  logger.info("Mode is already set correctly.")

# Call set_preset_mode based on home mode and time of day, using the service data above.
if home_mode == "Home":
  logger.info("In home mode.")
  if time_of_day == "dusk" or time_of_day == "night":
    logger.info("Home dusk or night.")
    hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "Sleep"}, False)
  else:
    logger.info("Home morning/day.")
    hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "Home"}, False)
elif home_mode == "Away":
  logger.info("Away mode.")
  hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "Away"}, False)
elif home_mode == "Sleep":
  logger.info("Sleep mode.")
  hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "Sleep"}, False)
else:
  logger.warn(f"No setting for {home_mode} home mode.")