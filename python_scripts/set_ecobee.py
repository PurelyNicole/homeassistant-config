# This script is designed to work with ecobee thermostats. It assumes the Comfort Settings are properly set within the Ecobee app.
logger.debug("Set Ecobee script is running.")

# Get thermostat to update
thermostat = data.get("thermostat")
weather = data.get("weather")

# Get forecast data
service_data = {"type": "daily", "entity_id": weather}
current_forecast = hass.services.call("weather", "get_forecasts", service_data, blocking=True, return_response=True)

# Get current home mode and forecasted high temperature for the day.
home_mode = (hass.states.get("input_select.home_mode")).state
current_mode = (hass.states.get(thermostat)).state
today_high = (current_forecast[weather]["forecast"][0]["temperature"])
window_satus = (hass.states.get("binary_sensor.windows")).state
peak_season = (hass.states.get("input_boolean.dte_peak_season")).state
peak_hours = (hass.states.get("schedule.dte_peak_hours")).state
current_month = datetime.datetime.now().month

def normalOperation():
  logger.info("Enter normal operation mode.")
  # Set thermostat mode based on forecasted high temperature.
  if today_high > 66:
    logger.info(f"Today's high: {today_high}. Setting mode to cool.")
    operation_mode = "cool"
  # Sets heat_cool variables.
  elif today_high > 55 and today_high <= 66:
    logger.info(f"Today's high: {today_high}. Setting mode to heat_cool.")
    operation_mode = "heat_cool"
  # Sets heat variables.
  elif today_high <= 55:
    logger.info(f"Today's high: {today_high}. Setting mode to heat.")
    operation_mode = "heat"
  else:
    logger.warn(f"Temperature {today_high} is out of range.")

  # Turn HVAC on/off based on window state.
  windowState(operation_mode)

  # Call set_preset_mode based on home mode and time of day, using the service data above.
  if home_mode == "Home":
    logger.info("People are home.")
    if hass.states.is_state("binary_sensor.night", "on") and operation_mode == "cool":
      logger.info("Nighttime when it's warm. Start sleep cooling early.")
      hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "sleep"}, False)
    else:    
      logger.info("It is not night. Set thermostat to home.")
      hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "home"}, False)
  elif home_mode == "Away":
    logger.info("Away mode.")
    hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "away"}, False)
  elif home_mode == "Sleep":
    logger.info("Sleep mode.")
    hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "sleep"}, False)
  else:
    logger.warn(f"No setting for {home_mode} home mode.")

def dtePeakSeasonMode():
  logger.info("Enter DTE Peak Season mode.")
  operation_mode = "cool"
  peak_hours_temp = 80
  current_hour = datetime.datetime.now().hour
  
  # Set pre-chill temperatures
  if today_high >= 75 and today_high <= 84:
    pre_chill_temp = 70
  elif today_high > 84:
    pre_chill_temp = 68
  else:
    pre_chill_temp = 72

  # Turn HVAC on/off based on window state.
  windowState(operation_mode)

  # Prechill before the peak hours start
  if current_hour >= 0 and current_hour < 7:
    logger.info("Extra cool for sleeping.")
    hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "sleep"}, False)
  elif current_hour >= 7 and current_hour < 15:
    logger.info("Prechilling the house")
    hass.services.call("climate", "set_temperature", {"entity_id": thermostat, "temperature": pre_chill_temp}, False)
  elif current_hour >=15 and current_hour < 19:
    logger.info("Entering peak hour mode.")
    hass.services.call("climate", "set_temperature", {"entity_id": thermostat, "temperature": peak_hours_temp}, False)
  elif current_hour >=19:
    logger.info("It's after 7. Start cooling bedroom.")
    hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": "sleep"}, False)
  else:
    logger.info(f"Current hour is {current_hour}. Return to normal operation.")
    normalOperation()

def windowState(operation_mode):
  if window_satus == "off":
    if current_mode != operation_mode:
      logger.info("Windows are closed. Setting operation mode.")
      hass.services.call("climate", "set_hvac_mode", {"entity_id": thermostat, "hvac_mode": operation_mode}, False)
      time.sleep(5) #wait to send command to set temp
  elif window_satus == "on":
    logger.info("Windows open. Set operation to off.")
    hass.services.call("climate", "set_hvac_mode", {"entity_id": thermostat, "hvac_mode": "off"}, False)
  else:
    logger.info("Mode is already set correctly.")

# Determine peak season
if peak_season == "on":
  logger.info("Prepare to enter peak season mode.")
  dtePeakSeasonMode()
else:
  logger.info("Prepare to enter normal mode.")
  normalOperation()