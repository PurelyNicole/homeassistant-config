# Choose the thermostats we're working with.
main_thermostat = data.get("main_thermostat")
fr_thermostat = data.get("fr_thermostat")

# Get the mode of main thermostat.
current_mode = (hass.states.get(main_thermostat)).state

# Set fr_thermostat based on main_thermost
if current_mode == "heat":
  set_temp = (hass.states.get(main_thermostat).attributes['temperature'])
  logger.info(f"Set operation to heat and temperature to {set_temp}.")
  hass.services.call("climate", "set_temperature", {"entity_id": fr_thermostat, "hvac_mode": "heat", "temperature": set_temp}, False)
elif current_mode == "heat_cool":
  set_temp = (hass.states.get(main_thermostat).attributes['target_temp_low'])
  logger.info(f"Set operation to heat and temperature to {set_temp}.")
  hass.services.call("climate", "set_temperature", {"entity_id": fr_thermostat, "hvac_mode": "heat", "temperature": set_temp}, False)
else:
  logger.info("Set operation to off.")
  hass.services.call("climate", "set_hvac_mode", {"entity_id": fr_thermostat, "hvac_mode": "off"}, False)