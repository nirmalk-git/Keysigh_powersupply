# # Import the package into whichever script is needed.
# import Keysight_E3631A as keysight
#
# # Create a power supply instance, it should automatically
# # connect and test the connection with a few commands
# # and beeps.
# power_supply = keysight.Keysight_E3631A(
#     port="COM7", baudrate=9600, parity=None, data=8, timeout=1, _sound=True
# )
#
# # The beep scpi command.
# beep_command = "SYSTem:BEEPer:IMMediate"
# # Remote operation command
# remote_command = "SYSTem:REMote"
# # Sending the beep command, we also capture the responce
# # from the power supply, here is an empty string.
# # The power supply should beep once you ran this instruction.
# response = power_supply.send_scpi_command(command=beep_command)


# import Keysight_E3631A as keysight
#
# serial_dict = {
#     "port": "COM7",
#     "baudrate": 9600,
#     "parity": "none",
#     "data": 8,
#     "timeout": 2,
# }
#
# limit_dict = {
#     "MIN_P6V_VOLTAGE": 0.0,
#     "MAX_P6V_VOLTAGE": 6.0,
#     "MIN_P25V_VOLTAGE": 0.0,
#     "MAX_P25V_VOLTAGE": 25.0,
#     "MIN_N25V_VOLTAGE": -25.0,
#     "MAX_N25V_VOLTAGE": 0.0,
# }
# # # Combine the two.
# config_dict = {**serial_dict, **limit_dict}
#
# # Create a power supply instance, it should automatically
# # connect and test the connection with a few commands
# # and beeps.
# power_supply = keysight.Keysight_E3631A.load_configuration(config_dict, _flat=False)
#
# # Set the voltage of the +6V/P6V output to 3 volts.
# power_supply.P6V_voltage = 3.5
# print(power_supply.P6V_voltage)  # Should print 3
#
# # Set the current of the +6V/P6V output to 1.42 amperes.
# power_supply.P6V_current = 1.0
# print(power_supply.P6V_current)  # Should print 1.42
