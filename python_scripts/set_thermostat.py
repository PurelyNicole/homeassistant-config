# Get thermostat to update
entity_id = data.get("entity_id")

# Get current home mode and forecasted high temperature for the day.
home_mode = (hass.states.get("input_select.home_mode")).state
today_high = (hass.states.get("sensor.dark_sky_daytime_high_temperature_0d")).state
current_mode = (hass.states.get("climate.living_room")).state

# Get current time of day.
if hass.states.is_state("binary_sensor.morning", "on"):
  logger.info("Morning.")
  time_of_day = "morning"
elif hass.states.is_state("binary_sensor.day", "on"):
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

# Set heat/cool variables based on forecasted high temperature.
# Sets cool variables.
if today_high > "80":
  logger.info("Setting mode to cool.")
  operation_mode = "cool"
  away_temp = 74
  home_temp = 72
  night_temp = 70
# Sets auto variables.
elif today_high >= "60" and today_high <= "80":
  logger.info("Setting mode to heat_cool.")
  operation_mode = "auto"
  away_high = 74
  away_low = 64
  home_high = 72
  home_low = 67
  night_high = 70
  night_low = 66
# Sets heat variables.
elif today_high < "60":
  logger.info("Setting mode to heat.")
  operation_mode = "heat"
  away_temp = 66
  home_temp = 68
  night_temp = 66
else:
  logger.warn("Temperature is out of range.")

# Set the service data for heat_cool mode
if operation_mode == "auto":
  service_data_home = {"entity_id": entity_id, "target_temp_high": home_high, "target_temp_low": home_low, "hvac_mode": operation_mode}
  service_data_away = {"entity_id": entity_id, "target_temp_high": away_high, "target_temp_low": away_low,"hvac_mode": operation_mode}
  service_data_night = {"entity_id": entity_id, "target_temp_high": night_high, "target_temp_low": night_low,"hvac_mode": operation_mode}
# Set the service data for all other modes
else:
  logger.info("Set non-auto data.")
  service_data_home = {"entity_id": entity_id, "temperature": home_temp, "hvac_mode": operation_mode,}
  service_data_away = {"entity_id": entity_id, "temperature": away_temp, "hvac_mode": operation_mode}
  service_data_night = {"entity_id": entity_id, "temperature": night_temp, "hvac_mode": operation_mode}

# For some reason, setting the mode with the set_temperature service is not working. This is a workaround until I know why.
if current_mode != operation_mode:
  logger.info("Set operation mode.")
  hass.services.call("climate", "set_hvac_mode", {"entity_id": entity_id, "hvac_mode": operation_mode}, False)
else:
  logger.info("Mode is already set correctly.")

# Call set_tempearture based on home mode and time of day, using the service data above.
if home_mode == "Home":
  logger.info("In home mode.")
  if time_of_day == "dusk" or time_of_day == "night":
    logger.info("Home dusk or night.")
    hass.services.call("climate", "set_temperature", service_data_night, False)
  else:
    logger.info("Home morning/day.")
    hass.services.call("climate", "set_temperature", service_data_home, False)
elif home_mode == "Away":
  logger.info("Away mode.")
  hass.services.call("climate", "set_temperature", service_data_away, False)
elif home_mode == "Sleep":
  logger.info("Sleep mode.")
  hass.services.call("climate", "set_temperature", service_data_night, False)
else:
  logger.warn(f"No setting for {home_mode} home mode.")
