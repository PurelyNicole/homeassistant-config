# This script is designed to work with ecobee thermostats. It assumes the Comfort Settings are properly set within the Ecobee app.
logger.debug("Script is running.")

# Get thermostat to update
thermostat = data.get("thermostat")
weather = data.get("weather")

# Get current home mode and forecasted high temperature for the day.
home_mode = (hass.states.get("input_select.home_mode")).state
current_mode = (hass.states.get(thermostat)).state
today_high = (hass.states.get(weather).attributes['forecast'][0]['temperature'])
window_satus = (hass.states.get("binary_sensor.windows")).state
peak_season = (hass.states.get("input_boolean.dte_peak_season")).state
peak_hours = (hass.states.get("schedule.dte_peak_hours")).state

def normalOperation():
  logger.info("Enter normal operation mode.")
  # Set thermostat mode based on forecasted high temperature.
  if today_high > 74:
    logger.info("Setting mode to cool.")
    operation_mode = "cool"
  # Sets heat_cool variables.
  elif today_high >= 55 and today_high <= 74:
    logger.info("Setting mode to heat_cool.")
    operation_mode = "heat_cool"
  # Sets heat variables.
  elif today_high < 55:
    logger.info("Setting mode to heat.")
    operation_mode = "heat"
  else:
    logger.warn("Temperature is out of range.")

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

  # Turn HVAC on/off based on window state.
  if window_satus == "off":
    if current_mode != operation_mode:
      logger.info("Windows are closed. Setting operation mode.")
      hass.services.call("climate", "set_hvac_mode", {"entity_id": thermostat, "hvac_mode": operation_mode}, False)
  elif window_satus == "on":
    logger.info("Windows open. Set operation to off.")
    hass.services.call("climate", "set_hvac_mode", {"entity_id": thermostat, "hvac_mode": "off"}, False)
  else:
    logger.info("Mode is already set correctly.")

def dtePeakSeasonMode():
  logger.info("Enter DTE Peak Season mode.")
  operation_mode = "cool"
  peak_hours_temp = 80
  current_hour = datetime.datetime.now().hour
  
  # Set pre-chill temperatures
  if today_high >= 75 and today_high <= 85:
    pre_chill_temp = 70
  elif today_high > 85:
    pre_chill_temp = 68
  else:
    logger.warn("You shouldn't be here.")

  # Prechill before the peak hours start
  if current_hour > 7 and current_hour < 15:
    logger.info("Prechilling the house")
    hass.services.call("climate", "set_temperature", {"entity_id": thermostat, "temperature": pre_chill_temp}, False)
  elif current_hour >=15 and current_hour < 19:
    logger.info("Entering peak hour mode.")
    hass.services.call("climate", "set_temperature", {"entity_id": thermostat, "temperature": peak_hours_temp}, False)
  else:
    logger.info("Returning to normal operation.")
    normalOperation()

# Determine peak season
if peak_season == "on" and today_high > 74:
  logger.info("Prepare to enter peak season mode.")
  dtePeakSeasonMode()
else:
  logger.info("Prepare to enter normal mode.")
  normalOperation()