# Import the package into whichever script is needed.
import Keysight_E3631A as keysight
# Create a power supply instance, it should automatically
# connect and test the connection with a few commands
# and beeps.
power_supply = keysight.Keysight_E3631A(
    port="COM7", baudrate=9600, parity=None, data=8, timeout=1, _sound=True
)

# Remote operation command
remote_command = "SYSTem:REMote"
# Sending the beep command, we also capture the responce
# from the power supply, here is an empty string.
# The power supply should beep once you ran this instruction.
response = power_supply.send_scpi_command(command=remote_command)


