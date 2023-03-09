# This script is designed to work with ecobee thermostats. It assumes the Comfort Settings are properly set within the Ecobee app.

# Get thermostat to update
thermostat = data.get("thermostat")
weather = data.get("weather")

# Get current home mode and forecasted high temperature for the day.
home_mode = (hass.states.get("input_select.home_mode")).state
current_mode = (hass.states.get(thermostat)).state
today_high = (hass.states.get(weather).attributes['forecast'][0]['temperature'])
window_satus = (hass.states.get("binary_sensor.windows")).state

# Set thermostat mode based on forecasted high temperature.
if today_high > 80:
  logger.info("Setting mode to cool.")
  operation_mode = "cool"
# Sets heat_cool variables.
elif today_high >= 55 and today_high <= 80:
  logger.info("Setting mode to heat_cool.")
  operation_mode = "heat_cool"
# Sets heat variables.
elif today_high < 55:
  logger.info("Setting mode to heat.")
  operation_mode = "heat"
else:
  logger.warn("Temperature is out of range.")

# Set the operation mode if the thermostat is not already in that mode.
if window_satus == "off":
  if current_mode != operation_mode:
    logger.info("Set operation mode.")
    hass.services.call("climate", "set_hvac_mode", {"entity_id": thermostat, "hvac_mode": operation_mode}, False)
elif window_satus == "on":
  logger.info("Set operation to off.")
  hass.services.call("climate", "set_hvac_mode", {"entity_id": thermostat, "hvac_mode": "off"}, False)
else:
  logger.info("Mode is already set correctly.")

# Call set_preset_mode based on home mode and time of day, using the service data above.
if home_mode == "Home":
  logger.info("In home mode.")
  hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "Home"}, False)
elif home_mode == "Away":
  logger.info("Away mode.")
  hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "Away"}, False)
elif home_mode == "Sleep":
  logger.info("Sleep mode.")
  hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "Sleep"}, False)
else:
  logger.warn(f"No setting for {home_mode} home mode.")