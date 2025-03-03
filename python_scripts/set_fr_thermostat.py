# Choose the thermostats we're working with.
main_thermostat = data.get("main_thermostat")
fr_thermostat = data.get("fr_thermostat")

# Get the mode of main thermostat.
current_mode = (hass.states.get(main_thermostat)).state
workday = (hass.states.get("binary_sensor.eric_workday_sensor")).state
dt = datetime.datetime.now()
day_of_week = dt.weekday()
current_hour = dt.hour

# Set fr_thermostat based on main_thermost
if ((current_mode != "cool") and (current_mode != "off")):
  logger.info("Ecobee is heat, set to heat mode.")
  if ((workday == "off") or (current_hour > 15)):
    logger.info("It's weekend/evening. Match ecobee temperature.")
    if (current_mode == "heat"):
      set_temp = (hass.states.get(main_thermostat).attributes['temperature'])
    elif (current_mode == "heat_cool"):
      set_temp = (hass.states.get(main_thermostat).attributes['target_temp_low'])
    else:
      logger.warn("Something went wrong, you shouldn't be here.")
  else:
    logger.info("Its a weekday morning. Set to 60.")
    set_temp = 60
  logger.info(f"Set operation to heat and temperature to {set_temp}.")
  hass.services.call("climate", "set_temperature", {"entity_id": fr_thermostat, "hvac_mode": "heat", "temperature": set_temp}, False)
elif (current_mode == "unavailable"):
  logger.warn("Ecobee offline. Make no changes.")
else:
  logger.info("Set operation to off.")
  hass.services.call("climate", "set_hvac_mode", {"entity_id": fr_thermostat, "hvac_mode": "off"}, False)