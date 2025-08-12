# This script is designed to work with ecobee thermostats. It assumes the Comfort Settings are properly set within the Ecobee app.
logger.debug("Set Ecobee script is running.")

# Get thermostat to update
thermostat = data.get("thermostat")
weather = data.get("weather")

# Get forecast data
service_data = {"type": "daily", "entity_id": weather}
current_forecast = hass.services.call("weather", "get_forecasts", service_data, blocking=True, return_response=True)

# Get variables that impact operating mode
home_mode = (hass.states.get("input_select.home_mode")).state
today_high = (current_forecast[weather]["forecast"][0]["temperature"])
window_status = (hass.states.get("binary_sensor.windows")).state
current_mode = (hass.states.get(thermostat)).state
guest_mode = (hass.states.get("input_boolean.guest_mode")).state
is_dusk = (hass.states.get("binary_sensor.dusk")).state
is_night = (hass.states.get("binary_sensor.night")).state

# Set thermostat mode based on forecasted high temperature.
def setOperationMode():
  if today_high > 70 and window_status == "off":
    logger.info(f"Today's high: {today_high}. Setting mode to cool.")
    operation_mode = "cool"
  elif today_high > 55 and today_high <= 70 and window_status == "off":
    logger.info(f"Today's high: {today_high}. Setting mode to heat_cool.")
    operation_mode = "heat_cool"
  elif today_high <= 55 and window_status == "off":
    logger.info(f"Today's high: {today_high}. Setting mode to heat.")
    operation_mode = "heat"
  elif window_status == "on":
    logger.info("Windows are open. Setting mode to off.")
    operation_mode = "off"
  else:
    logger.error(f"Temperature {today_high} is out of range.")

  return operation_mode

# Set the preset mode, the values of preset modes are set in ecobee app.
def setPresetMode():
  if home_mode == "Home":
    logger.info("People are home.")
    if (is_dusk == "on" or is_night== "on") and operation_mode == "cool":
      logger.info("Nighttime when it's warm. Set preset to sleep.")
      preset_mode = "sleep"
    else:
      logger.info("It is not night. Set thermostat to home.")
      preset_mode = "home"
  elif home_mode == "Away":
    logger.info("Away mode.")
    preset_mode = "away"
  elif home_mode == "Sleep" or home_mode == "Wind Down":
    logger.info("Sleep mode.")
    preset_mode = "sleep"
  else:
    logger.error(f"No setting for {home_mode} home mode.")

  return preset_mode

# If the thermostat isn't running in the correct operation mode, set it.
def callThermostatSetHvacMode(operation_mode):
  if current_mode != operation_mode:
    logger.info(f"Setting HVAC to {operation_mode}")
    hass.services.call("climate", "set_hvac_mode", {"entity_id": thermostat, "hvac_mode": operation_mode}, False)
  else:
    logger.info("HVAC is already set to correct mode.")

# If the operation mode is not off, send the preset mode to thermostat.
def callThermostatSetPresetMode(preset_mode):
  if operation_mode != "off":
    logger.info(f"Setting preset mode to {preset_mode}")
    hass.services.call("climate", "set_preset_mode", {"entity_id": thermostat, "preset_mode": preset_mode}, False)
  else:
    logger.info("Operation mode is off. Not sending a preset mode.")

operation_mode = setOperationMode()
callThermostatSetHvacMode(operation_mode)
preset_mode = setPresetMode()
callThermostatSetPresetMode(preset_mode)

# TODO: Add logic for kicking on AC with solar. If Current mode is Cool and Current Net Power Consumption < -?? set HVAC to current setpoint minus 1 degree
# If Current Net Power Consumption > 1 and temperature < 72, set to 72