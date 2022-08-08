
import copy
import math
import sys
import warnings

import serial

# These are constant values used for checking and establishing 
# power supply limits.
# These values are obtained from the factory manufactor. See 
# http://literature.cdn.keysight.com/litweb/pdf/E3631-90002.pdf#page=186&zoom=100,177,108
_FACTORY_MIN_P6V_VOLTAGE = 0.0
_FACTORY_MAX_P6V_VOLTAGE = 6.0
_FACTORY_MIN_P25V_VOLTAGE = 0.0
_FACTORY_MAX_P25V_VOLTAGE = 25.0
_FACTORY_MIN_N25V_VOLTAGE = -25.0
_FACTORY_MAX_N25V_VOLTAGE = 0.0

_FACTORY_MIN_P6V_CURRENT = 0.0
_FACTORY_MAX_P6V_CURRENT = 5.0
_FACTORY_MIN_P25V_CURRENT = 0.0
_FACTORY_MAX_P25V_CURRENT = 1.0
_FACTORY_MIN_N25V_CURRENT = 0.0
_FACTORY_MAX_N25V_CURRENT = 1.0
# These values are user created limitations to the output of the
# power supply. Default to the factory limitations.
USER_MIN_P6V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_P6V_VOLTAGE)
USER_MAX_P6V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_P6V_VOLTAGE)
USER_MIN_P25V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_P25V_VOLTAGE)
USER_MAX_P25V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_P25V_VOLTAGE)
USER_MIN_N25V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_N25V_VOLTAGE)
USER_MAX_N25V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_N25V_VOLTAGE)

USER_MIN_P6V_CURRENT = copy.deepcopy(_FACTORY_MIN_P6V_CURRENT)
USER_MAX_P6V_CURRENT = copy.deepcopy(_FACTORY_MAX_P6V_CURRENT)
USER_MIN_P25V_CURRENT = copy.deepcopy(_FACTORY_MIN_P25V_CURRENT)
USER_MAX_P25V_CURRENT = copy.deepcopy(_FACTORY_MAX_P25V_CURRENT)
USER_MIN_N25V_CURRENT = copy.deepcopy(_FACTORY_MIN_N25V_CURRENT)
USER_MAX_N25V_CURRENT = copy.deepcopy(_FACTORY_MAX_N25V_CURRENT)

# Default timeout value.
DEFAULT_TIMEOUT = 15
# The number of resolved digits kept by internal rounding
# by the power supply.
_SUPPLY_RESOLVED_DIGITS = 4

class Keysight_E3631A():
    """ This is a class that acts as a control for the 
    Keysight_E3631A power supply.

    Attributes
    ----------
    P6V_voltage : property(float)
        The attribute that controls the P6V output voltage on the 
        power supply.
    P6V_current : property(float)
        The attribute that controls the P6V output current on the 
        power supply.
    P25V_voltage : property(float)
        The attribute that controls the P25V output voltage on the 
        power supply.
    P25V_current : property(float)
        The attribute that controls the P25V output current on the 
        power supply.
    N25V_voltage : property(float)
        The attribute that controls the N25V output voltage on the 
        power supply.
    N25V_current : property(float)
        The attribute that controls the N25V output current on the 
        power supply.

    MIN_P6V_VOLTAGE : float
        The minimum instance limitation for P6V voltages.
    MAX_P6V_VOLTAGE : float
        The maximum instance limitation for P6V voltages.
    MIN_P25V_VOLTAGE : float
        The minimum instance limitation for P25V voltages.
    MAX_P25V_VOLTAGE : float
        The maximum instance limitation for P25V voltages.
    MIN_N25V_VOLTAGE : float
        The minimum instance limitation for N25V voltages.
    MAX_N25V_VOLTAGE : float
        The maximum instance limitation for N25V voltages.

    MIN_P6V_CURRENT : float
        The minimum instance limitation for P6V currents.
    MAX_P6V_CURRENT : float
        The maximum instance limitation for P6V currents.
    MIN_P25V_CURRENT : float
        The minimum instance limitation for P25V currents.
    MAX_P25V_CURRENT : float
        The maximum instance limitation for P25V currents.
    MIN_N25V_CURRENT : float
        The minimum instance limitation for N25V currents.
    MAX_N25V_CURRENT : float
        The maximum instance limitation for N25V currents.

    local : function
        Alias to `Keysight_E3631A.local_mode()`
    remote : function
        Alias to `Keysight_E3631A.remote_mode()`
    command, send, write : function
        Aliases to `Keysight_E3631A.send_scpi_command()`
    _raw, _send_raw : function
        Aliases to `_send_raw_scpi_command()`
    """

    # Internal implimentation values.
    _P6V_voltage = float()
    _P25V_voltage = float()
    _N25V_voltage = float()
    _P6V_current = float()
    _P25V_current = float()
    _N25V_current = float()

    # Serial connection information.
    _serial_port = str()
    _serial_baudrate = int()
    _serial_parity = str()
    _serial_data = int()
    _serial_start = int()
    _serial_end = int()
    _serial_timeout = int()

    # These values are user created limitations to the output of the
    # power supply for each individual power supply instance. 
    # Default to the factory limitations.
    MIN_P6V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_P6V_VOLTAGE)
    MAX_P6V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_P6V_VOLTAGE)
    MIN_P25V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_P25V_VOLTAGE)
    MAX_P25V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_P25V_VOLTAGE)
    MIN_N25V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_N25V_VOLTAGE)
    MAX_N25V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_N25V_VOLTAGE)

    MIN_P6V_CURRENT = copy.deepcopy(_FACTORY_MIN_P6V_CURRENT)
    MAX_P6V_CURRENT = copy.deepcopy(_FACTORY_MAX_P6V_CURRENT)
    MIN_P25V_CURRENT = copy.deepcopy(_FACTORY_MIN_P25V_CURRENT)
    MAX_P25V_CURRENT = copy.deepcopy(_FACTORY_MAX_P25V_CURRENT)
    MIN_N25V_CURRENT = copy.deepcopy(_FACTORY_MIN_N25V_CURRENT)
    MAX_N25V_CURRENT = copy.deepcopy(_FACTORY_MAX_N25V_CURRENT)


    def __init__(self, port, baudrate=9600, parity=None, data=8,
                 timeout=DEFAULT_TIMEOUT, _sound=True):
        """ Creating the power supply instance. If successful, the 
        power supply will be put into remote mode automatically.
        It will also send a few test commands and beep.

        Parameters
        ----------
        port : string
            The port string, value, or name that the power supply
            is connected to.
        baudrate : int
            The baudrate that the power supply is set to. Default
            from the factory is 9600.
        parity : string
            The parity bit setting the power supply is set to. Must
            be one of the following: 'none' (factory default), 'even'
            'odd'.
        data : int
            The data bit setting the power supply is set to. Factory
            default is 8.
        timeout : int
            The timeout, in seconds, that this class will wait for
            a responce from the power supply when a command is sent.
            Default is an axiomatic 15 seconds.
        _sound : boolean (optional)
            The power supply will not send the test beeps if this
            is False. Defaults to True.

        Returns
        -------
        None
        """
        # Assign parity based on entry.
        parity = str(parity).lower() if (parity is not None) else 'none'
        if (parity == 'none'):
            parity = serial.PARITY_NONE
        elif (parity == 'even'):
            parity = serial.PARITY_EVEN
        elif (parity == 'odd'):
            parity = serial.PARITY_ODD
        else:
            # Parity can only be None, Even, or Odd for this 
            # instrument.
            raise ValueError("The parity must be either: "
                             "'none', 'even', or 'odd'.")
                        
        # Ensure that the timeout value is at least one second.
        if (timeout < 1.0):
            # We will force it to be the default.
            warnings.warn("The timeout must be at least 1 second. Choosing "
                          "default of 15 seconds.",
                          RuntimeWarning, stacklevel=2)
            timeout = DEFAULT_TIMEOUT

        # Assign the serial connection information.
        self._serial_port = str(port)
        self._serial_baudrate = int(baudrate)
        self._serial_parity = parity
        self._serial_data = int(data)
        self._serial_timeout = int(timeout)
        # These are set by Keysight hardware and are unchangeable.
        # See http://literature.cdn.keysight.com/litweb/pdf/E3631-90002.pdf#page=73&zoom=100,177,108
        self._serial_start = int(1)
        self._serial_end = int(2)

        # Load up the serial connection and send a test command.
        if ((len(self.version()) == 0) and 
            (len(self.send_scpi_command('*IDN?')) == 0)):
            # There was no responce to the system version command.
            # There does not seem to be a Keysight E3631A 
            # attached to this interface.
            warnings.warn("There is no responce from the port `{port}`. "
                          "The instrument may not be communicating back "
                          "with this class. Some functions may fail."
                          .format(port=self._serial_port),
                          RuntimeWarning, stacklevel=2)
        else:
            # Set the system into remote mode.
            __ = self.remote_mode()

        # Attempt the melody for confirmation and to also test 
        # out the timeout.
        if (_sound):
            # Beeping three times for confirmation of the class 
            # properly sending a command to the supply.
            __ = self.beep()
            __ = self.beep()
            __ = self.beep()
        else:
            # The user does not want any fun, or prefers the silence.
            pass
        # All done?
        return None

    # This allows a configuration dictionary to be used.
    @classmethod
    def load_configuration(self, configuration, _flat=False):
        """ This is a function that allows the usage of a 
        dictionary to specify the parameters of the class. The 
        configuration file can be found in the repository.

        Parameters
        ----------
        configuration : dictionary-like
            The configuration dictionary. It must contain the 
            required parameters, else an error will be raised. If
            the limitation paramters are not there, the factory
            defaults will be used instead.
        _flat : boolean (optional)
            Flaten the dictionary before processing. Defaults to 
            False.

        Returns
        -------
        power_supply : Keysight_E3631A
            A Keysight_E3631A class based on the configuration
            parameters.
        """
        # Flatten the dictionary.
        if (_flat):
            config = _ravel_dictionary(
                dictionary=dict(configuration), conflict='raise')
        else:
            config = dict(configuration)

        # Attempt to obtain the serial parameters.
        try:
            port = config['port']
            baudrate = config['baudrate']
            parity = config['parity']
            data = config['data']
            timeout = config['timeout']
        except KeyError:
            raise KeyError("The serial parameters are missing. Required are "
                           "the following: 'port', 'baudrate', 'parity', "
                           "'data' and 'timeout'.")
        # Attempt to obtain the limitation parameters. Default to
        # factory. 
        MIN_P6V_VOLTAGE = config.get('MIN_P6V_VOLTAGE', 
                                     _FACTORY_MIN_P6V_VOLTAGE)
        MAX_P6V_VOLTAGE = config.get('MAX_P6V_VOLTAGE', 
                                   _FACTORY_MAX_P6V_VOLTAGE)
        MIN_P25V_VOLTAGE = config.get('MIN_P25V_VOLTAGE', 
                                      _FACTORY_MIN_P25V_VOLTAGE)
        MAX_P25V_VOLTAGE = config.get('MAX_P25V_VOLTAGE', 
                                      _FACTORY_MAX_P25V_VOLTAGE)
        MIN_N25V_VOLTAGE = config.get('MIN_N25V_VOLTAGE', 
                                      _FACTORY_MIN_N25V_VOLTAGE)
        MAX_N25V_VOLTAGE = config.get('MAX_N25V_VOLTAGE', 
                                      _FACTORY_MAX_N25V_VOLTAGE)

        MIN_P6V_CURRENT = config.get('MIN_P6V_CURRENT', 
                                    _FACTORY_MIN_P6V_CURRENT)
        MAX_P6V_CURRENT = config.get('MAX_P6V_CURRENT', 
                                      _FACTORY_MAX_P6V_CURRENT)
        MIN_P25V_CURRENT = config.get('MIN_P25V_CURRENT', 
                                      _FACTORY_MIN_P25V_CURRENT)
        MAX_P25V_CURRENT = config.get('MAX_P25V_CURRENT', 
                                      _FACTORY_MAX_P25V_CURRENT)
        MIN_N25V_CURRENT = config.get('MIN_N25V_CURRENT', 
                                      _FACTORY_MIN_N25V_CURRENT)
        MAX_N25V_CURRENT = config.get('MAX_N25V_CURRENT', 
                                      _FACTORY_MAX_N25V_CURRENT)

        # Create the instance.
        power_supply = Keysight_E3631A(port=port, baudrate=baudrate,
                                       parity=parity, data=data, 
                                       timeout=timeout)

        # Assign the limitations.
        power_supply.MIN_P6V_VOLTAGE = MIN_P6V_VOLTAGE
        power_supply.MAX_P6V_VOLTAGE = MAX_P6V_VOLTAGE
        power_supply.MIN_P25V_VOLTAGE = MIN_P25V_VOLTAGE
        power_supply.MAX_P25V_VOLTAGE = MAX_P25V_VOLTAGE
        power_supply.MIN_N25V_VOLTAGE = MIN_N25V_VOLTAGE
        power_supply.MAX_N25V_VOLTAGE = MAX_N25V_VOLTAGE

        power_supply.MIN_P6V_CURRENT = MIN_P6V_CURRENT
        power_supply.MAX_P6V_CURRENT = MAX_P6V_CURRENT
        power_supply.MIN_P25V_CURRENT = MIN_P25V_CURRENT
        power_supply.MAX_P25V_CURRENT = MAX_P25V_CURRENT
        power_supply.MIN_N25V_CURRENT = MIN_N25V_CURRENT
        power_supply.MAX_N25V_CURRENT = MAX_N25V_CURRENT

        return power_supply
    

    # Sends a beep command.
    def beep(self):
        """ Sends a beep command to the power supply.

        Parameters
        ----------
        None

        Returns
        -------
        responce : string
            The responce from the power supply.
        """
        # The beep scpi command.
        beep_command = 'SYSTem:BEEPer:IMMediate'
        # Sending the beep command.
        responce = self.send_scpi_command(command=beep_command)
        # All done.
        return responce

    # SCPI command for the version.
    def version(self):
        """ This sends a command to fetch the current version of
        the SCPI protocol.

        Parameters
        ----------
        None

        Returns
        -------
        responce : string
            The responce from the power supply, here it is likely
            the version number.
        """
        # Send the command.
        version_command = 'SYSTem:VERSion?'
        responce = self.send_scpi_command(command=version_command)
        # All done.
        return responce

    # SCPI command to fetch the first error in the queue.
    def error(self):
        """ This sends a command to fetch the current error. The 
        error queue is a first-in-first-out type of queue. A
        maximum of 20 errors can be stored in the error queue.

        Parameters
        ----------
        None

        Returns
        -------
        responce : string
            The responce from the power supply, here it is likely
            the current error.
        """
        # Send the command.
        error_command = 'SYSTem:ERRor?'
        responce = self.send_scpi_command(command=error_command)
        # All done.
        return responce
    # SCPI command to clear the entire register.
    def clear(self):
        """ This sends a command to clear the current register, 
        including clearing out errors. 

        Parameters
        ----------
        None

        Returns
        -------
        responce : string
            The responce from the power supply.
        """
        # Send the command.
        clear_command = '*CLS'
        responce = self.send_scpi_command(command=clear_command)
        # All done.
        return responce

    # This allows the power supply to be put into remote or local
    # mode. The local button still overrides.
    def remote_mode(self):
        """ This function sends a command to the power supply to 
        put it in remote mode. Remote mode means it is controlled by 
        this class. 
        
        Parameters
        ----------
        None

        Returns
        -------
        responce : string
            The responce from the power supply.
        """
        # Send the remote mode command to the power supply.
        remote_command = 'SYSTem:REMote'
        responce = self.send_scpi_command(command=remote_command)
        # All done.
        return responce
    def local_mode(self):
        """ This function sends a command to the power supply to 
        put it in local mode. Local mode means it is controlled by 
        the front interface.

        Parameters
        ----------
        None

        Returns
        -------
        responce : string
            The responce from the power supply.
        """
        # Send the local mode command to the power supply.
        local_command = 'SYSTem:LOCal'
        responce = self.send_scpi_command(command=local_command)
        # All done.
        return responce
    # Aliases...
    local = local_mode
    remote = remote_mode

    # The implementation for the 6V output for the power supply.
    def get_P6V_voltage(self):
        """ This gets the voltage of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='P6V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        volt, __ = result.split(',')
        volt = volt.strip('"')
        supply_voltage = float(volt)
        # Double check that the two voltages are the same.
        assert_bool = math.isclose(supply_voltage, self._P6V_voltage)
        assert_message = ("The supply P6V voltage and the class voltage "
                          "are not the same. Assign a voltage via "
                          "the class before reading the voltage. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_volt}  Power Supply: {ps_volt}"
                          .format(cls_volt=self._P6V_voltage,
                                  ps_volt=supply_voltage))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_voltage
    def set_P6V_voltage(self, volt):
        """ Sets the voltage of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal. 
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_P6V_VOLTAGE <= volt <= _FACTORY_MAX_P6V_VOLTAGE):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the factory specifications for the "
                             "P6V output: {min} <= V <= {max}."
                             .format(volt=volt, min=_FACTORY_MIN_P6V_VOLTAGE, 
                                     max=_FACTORY_MAX_P6V_VOLTAGE))
        # Ensure that the voltage value is not outside the user 
        # defined limits.
        if (USER_MIN_P6V_VOLTAGE <= volt <= USER_MAX_P6V_VOLTAGE):
            # The voltage is within the user's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the user limitations for the "
                             "P6V output: {min} <= V <= {max}."
                             .format(volt=volt, min=USER_MIN_P6V_VOLTAGE, 
                                     max=USER_MAX_P6V_VOLTAGE))
        # Ensure that the voltage value is not outside the object 
        # instance defined limits.
        if (self.MIN_P6V_VOLTAGE <= volt <= self.MAX_P6V_VOLTAGE):
            # The voltage is within the instance's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the instance limitations for the "
                             "P6V output: {min} <= V <= {max}."
                             .format(volt=volt, min=self.MIN_P6V_VOLTAGE, 
                                     max=self.MAX_P6V_VOLTAGE))
        # The power supply only supports a rounded voltage value to
        # the 3rd decimal point.
        volt = round(volt, _SUPPLY_RESOLVED_DIGITS)
        # The voltage passed the internal checks for safety. It can
        # be applied.
        self._P6V_voltage = volt
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='P6V', voltage=self._P6V_voltage, 
            current=self._P6V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_P6V_voltage(self):
        """ This is the deletion method for this power supply's 
        voltage. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the voltage.
        raise RuntimeError("You cannot delete the P6V voltage of "
                           "your power supply.")
        return None
    # The user interface of the voltage.
    P6V_voltage = property(get_P6V_voltage, set_P6V_voltage, 
                           del_P6V_voltage)
    def get_P6V_current(self):
        """ This gets the current of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='P6V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        __, curr = result.split(',')
        curr = curr.strip('"')
        supply_current = float(curr)
        # Double check that the two currents are the same.
        assert_bool = math.isclose(supply_current, self._P6V_current)
        assert_message = ("The supply P6V current and the class current "
                          "are not the same. Assign a current via "
                          "the class before reading the current. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_curr}  Power Supply: {ps_curr}"
                          .format(cls_curr=self._P6V_current,
                                  ps_curr=supply_current))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_current
    def set_P6V_current(self, curr):
        """ Sets the current of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal. 
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_P6V_CURRENT <= curr <= _FACTORY_MAX_P6V_CURRENT):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the factory specifications for the "
                             "P6V output: {min} <= I <= {max}."
                             .format(curr=curr, min=_FACTORY_MIN_P6V_CURRENT, 
                                     max=_FACTORY_MAX_P6V_CURRENT))
        # Ensure that the current value is not outside the user 
        # defined limits.
        if (USER_MIN_P6V_CURRENT <= curr <= USER_MAX_P6V_CURRENT):
            # The current is within the user's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the user limitations for the "
                             "P6V output: {min} <= I <= {max}."
                             .format(curr=curr, min=USER_MIN_P6V_CURRENT, 
                                     max=USER_MAX_P6V_CURRENT))
        # Ensure that the current value is not outside the object 
        # instance defined limits.
        if (self.MIN_P6V_CURRENT <= curr <= self.MAX_P6V_CURRENT):
            # The current is within the instance's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the instance limitations for the "
                             "P6V output: {min} <= I <= {max}."
                             .format(curr=curr, min=self.MIN_P6V_CURRENT, 
                                     max=self.MAX_P6V_CURRENT))
        # The power supply only supports a rounded current value to
        # the 3rd decimal point.
        curr = round(curr, _SUPPLY_RESOLVED_DIGITS)
        # The current passed the internal checks for safety. It can
        # be applied.
        self._P6V_current = curr
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='P6V', voltage=self._P6V_voltage, 
            current=self._P6V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_P6V_current(self):
        """ This is the deletion method for this power supply's 
        current. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the current.
        raise RuntimeError("You cannot delete the P6V current of "
                           "your power supply.")
        return None
    # The user interface of the current.
    P6V_current = property(get_P6V_current, set_P6V_current, 
                           del_P6V_current)

    # The implementation for the +25V output for the power supply.
    def get_P25V_voltage(self):
        """ This gets the voltage of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='P25V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        volt, __ = result.split(',')
        volt = volt.strip('"')
        supply_voltage = float(volt)
        # Double check that the two voltages are the same.
        assert_bool = math.isclose(supply_voltage, self._P25V_voltage)
        assert_message = ("The supply P25V voltage and the class voltage "
                          "are not the same. Assign a voltage via "
                          "the class before reading the voltage. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_volt}  Power Supply: {ps_volt}"
                          .format(cls_volt=self._P25V_voltage,
                                  ps_volt=supply_voltage))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_voltage
    def set_P25V_voltage(self, volt):
        """ Sets the voltage of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal.
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_P25V_VOLTAGE <= volt <= _FACTORY_MAX_P25V_VOLTAGE):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the factory specifications for the "
                             "P25V output: {min} <= V <= {max}."
                             .format(volt=volt, min=_FACTORY_MIN_P25V_VOLTAGE, 
                                     max=_FACTORY_MAX_P25V_VOLTAGE))
        # Ensure that the voltage value is not outside the user 
        # defined limits.
        if (USER_MIN_P25V_VOLTAGE <= volt <= USER_MAX_P25V_VOLTAGE):
            # The voltage is within the user's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the user limitations for the "
                             "P25V output: {min} <= V <= {max}."
                             .format(volt=volt, min=USER_MIN_P25V_VOLTAGE, 
                                     max=USER_MAX_P25V_VOLTAGE))
        # Ensure that the voltage value is not outside the object 
        # instance defined limits.
        if (self.MIN_P25V_VOLTAGE <= volt <= self.MAX_P25V_VOLTAGE):
            # The voltage is within the instance's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the instance limitations for the "
                             "P25V output: {min} <= V <= {max}."
                             .format(volt=volt, min=self.MIN_P25V_VOLTAGE, 
                                     max=self.MAX_P25V_VOLTAGE))
        # The power supply only supports a rounded voltage value to
        # the 3rd decimal point.
        volt = round(volt, _SUPPLY_RESOLVED_DIGITS)
        # The voltage passed the internal checks for safety. It can
        # be applied.
        self._P25V_voltage = volt
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='P25V', voltage=self._P25V_voltage, 
            current=self._P25V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_P25V_voltage(self):
        """ This is the deletion method for this power supply's 
        voltage. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the voltage.
        raise RuntimeError("You cannot delete the P25V voltage of "
                           "your power supply.")
        return None
    # The user interface of the voltage.
    P25V_voltage = property(get_P25V_voltage, set_P25V_voltage,
                            del_P25V_voltage)
    def get_P25V_current(self):
        """ This gets the current of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='P25V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        __, curr = result.split(',')
        curr = curr.strip('"')
        supply_current = float(curr)
        # Double check that the two currents are the same.
        assert_bool = math.isclose(supply_current, self._P25V_current)
        assert_message = ("The supply P25V current and the class current "
                          "are not the same. Assign a current via "
                          "the class before reading the current. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_curr}  Power Supply: {ps_curr}"
                          .format(cls_curr=self._P25V_current,
                                  ps_curr=supply_current))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_current
    def set_P25V_current(self, curr):
        """ Sets the current of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal. 
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_P25V_CURRENT <= curr <= _FACTORY_MAX_P25V_CURRENT):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the factory specifications for the "
                             "P25V output: {min} <= I <= {max}."
                             .format(curr=curr, min=_FACTORY_MIN_P25V_CURRENT, 
                                     max=_FACTORY_MAX_P25V_CURRENT))
        # Ensure that the current value is not outside the user 
        # defined limits.
        if (USER_MIN_P25V_CURRENT <= curr <= USER_MAX_P25V_CURRENT):
            # The current is within the user's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the user limitations for the "
                             "P25V output: {min} <= I <= {max}."
                             .format(curr=curr, min=USER_MIN_P25V_CURRENT, 
                                     max=USER_MAX_P25V_CURRENT))
        # Ensure that the current value is not outside the object 
        # instance defined limits.
        if (self.MIN_P25V_CURRENT <= curr <= self.MAX_P25V_CURRENT):
            # The current is within the instance's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the instance limitations for the "
                             "P25V output: {min} <= I <= {max}."
                             .format(curr=curr, min=self.MIN_P25V_CURRENT, 
                                     max=self.MAX_P25V_CURRENT))
        # The power supply only supports a rounded current value to
        # the 3rd decimal point.
        curr = round(curr, _SUPPLY_RESOLVED_DIGITS)
        # The current passed the internal checks for safety. It can
        # be applied.
        self._P25V_current = curr
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='P25V', voltage=self._P25V_voltage, 
            current=self._P25V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_P25V_current(self):
        """ This is the deletion method for this power supply's 
        current. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the current.
        raise RuntimeError("You cannot delete the P25V current of "
                           "your power supply.")
        return None
    # The user interface of the current.
    P25V_current = property(get_P25V_current, set_P25V_current, 
                            del_P25V_current)

    # The implementation for the -25V output for the power supply.
    def get_N25V_voltage(self):
        """ This gets the voltage of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='N25V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        volt, __ = result.split(',')
        volt = volt.strip('"')
        supply_voltage = float(volt)
        # Double check that the two voltages are the same.
        assert_bool = math.isclose(supply_voltage, self._N25V_voltage)
        assert_message = ("The supply N25V voltage and the class voltage "
                          "are not the same. Assign a voltage via "
                          "the class before reading the voltage. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_volt}  Power Supply: {ps_volt}"
                          .format(cls_volt=self._N25V_voltage,
                                  ps_volt=supply_voltage))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_voltage
    def set_N25V_voltage(self, volt):
        """ Sets the voltage of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal.
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_N25V_VOLTAGE <= volt <= _FACTORY_MAX_N25V_VOLTAGE):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the factory specifications for the "
                             "N25V output: {min} <= V <= {max}."
                             .format(volt=volt, min=_FACTORY_MIN_N25V_VOLTAGE, 
                                     max=_FACTORY_MAX_N25V_VOLTAGE))
        # Ensure that the voltage value is not outside the user 
        # defined limits.
        if (USER_MIN_N25V_VOLTAGE <= volt <= USER_MAX_N25V_VOLTAGE):
            # The voltage is within the users's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the user limitations for the "
                             "N25V output: {min} <= V <= {max}."
                             .format(volt=volt, min=USER_MIN_N25V_VOLTAGE, 
                                     max=USER_MAX_N25V_VOLTAGE))
        # Ensure that the voltage value is not outside the object 
        # instance defined limits.
        if (self.MIN_N25V_VOLTAGE <= volt <= self.MAX_N25V_VOLTAGE):
            # The voltage is within the instance's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the instance limitations for the "
                             "N25V output: {min} <= V <= {max}."
                             .format(volt=volt, min=self.MIN_N25V_VOLTAGE, 
                                     max=self.MAX_N25V_VOLTAGE))
        # The power supply only supports a rounded voltage value to
        # the 3rd decimal point.
        volt = round(volt, _SUPPLY_RESOLVED_DIGITS)
        # The voltage passed the internal checks for safety. It can
        # be applied.
        self._N25V_voltage = volt
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='N25V', voltage=self._N25V_voltage, 
            current=self._N25V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_N25V_voltage(self):
        """ This is the deletion method for this power supply's 
        voltage. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the voltage.
        raise RuntimeError("You cannot delete the N25V voltage of "
                           "your power supply.")
        return None
    # The user interface of the voltage.
    N25V_voltage = property(get_N25V_voltage, set_N25V_voltage, 
                            del_N25V_voltage)
    def get_N25V_current(self):
        """ This gets the current of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='N25V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        __, curr = result.split(',')
        curr = curr.strip('"')
        supply_current = float(curr)
        # Double check that the two currents are the same.
        assert_bool = math.isclose(supply_current, self._N25V_current)
        assert_message = ("The supply N25V current and the class current "
                          "are not the same. Assign a current via "
                          "the class before reading the current. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_curr}  Power Supply: {ps_curr}"
                          .format(cls_curr=self._N25V_current,
                                  ps_curr=supply_current))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_current
    def set_N25V_current(self, curr):
        """ Sets the current of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal. 
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_N25V_CURRENT <= curr <= _FACTORY_MAX_N25V_CURRENT):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the factory specifications for the "
                             "N25V output: {min} <= I <= {max}."
                             .format(curr=curr, min=_FACTORY_MIN_N25V_CURRENT, 
                                     max=_FACTORY_MAX_N25V_CURRENT))
        # Ensure that the current value is not outside the user 
        # defined limits.
        if (USER_MIN_N25V_CURRENT <= curr <= USER_MAX_N25V_CURRENT):
            # The current is within the user's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the user limitations for the "
                             "N25V output: {min} <= I <= {max}."
                             .format(curr=curr, min=USER_MIN_N25V_CURRENT, 
                                     max=USER_MAX_N25V_CURRENT))
        # Ensure that the current value is not outside the object 
        # instance defined limits.
        if (self.MIN_N25V_CURRENT <= curr <= self.MAX_N25V_CURRENT):
            # The current is within the instance's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the instance limitations for the "
                             "N25V output: {min} <= I <= {max}."
                             .format(curr=curr, min=self.MIN_N25V_CURRENT, 
                                     max=self.MAX_N25V_CURRENT))
        # The power supply only supports a rounded current value to
        # the 3rd decimal point.
        curr = round(curr, _SUPPLY_RESOLVED_DIGITS)
        # The current passed the internal checks for safety. It can
        # be applied.
        self._N25V_current = curr
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='N25V', voltage=self._N25V_voltage, 
            current=self._N25V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_N25V_current(self):
        """ This is the deletion method for this power supply's 
        current. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the current.
        raise RuntimeError("You cannot delete the N25V current of "
                           "your power supply.")
        return None
    # The user interface of the current.
    N25V_current = property(get_N25V_current, set_N25V_current, 
                            del_N25V_current)

    # This command fetches which instrument output is selected.
    def selected_output(self):
        """ This function sends a command to the instrument to
        see what is the current specified active output.

        Parameters
        ----------
        None

        Returns
        -------
        responce : string
            The responce from the power supply, here it is the output 
            that is currently selected.
        """
        # The command to get the current selected output.
        output_select_command = 'INSTrument:SELect?'
        responce = self.send_scpi_command(command=output_select_command)
        # All done.
        return responce

    # These functions handle the command interface of the serial
    # connection.
    def send_scpi_command(self, command, _escape=False):
        """ This function is a wrapper around sending a scpi command
        to the power supply. It performs internal checks to ensure 
        that the command send it proper. However, there are no
        checks here on the reasonableness of the command.

        The newline characters are automatically added to the 
        command sent and removed from the responce returned. Treat
        the input and output as normal strings.

        Parameters
        ----------
        command : string
            The SCPI command to be sent to the power supply.
        _escape : boolean (optional)
            Setting this to True disables error checking.

        Returns
        -------
        responce : string
            The responce from the power supply from the provided 
            command.
        """
        # The command must be suffixed with a new line for the 
        # power supply to properly recognize it.
        newline_command = ''.join([command, '\n'])

        # The most cross-platform solution is to just use the
        # default bytestring. Windows does not like simple strings.
        byte_command = bytearray(newline_command, sys.getdefaultencoding())
        # Send the command and read back the responce.
        raw_responce = self._send_raw_scpi_command(bytestring=byte_command)
        responce = str(raw_responce.decode())
        # The responce usually has the endline, removing it.
        suffix = '\r\n'
        if responce.endswith(suffix):
            responce = responce[:-len(suffix)]
        else:
            responce = responce

        # This allows for the skipping of an error check.
        # It should be used for internal use only.
        if (_escape):
            return responce
        else:
            # Test if the command instead created an error. If
            # it did, return the error instead.
            no_error_string = '+0,"No error"'
            if (responce == no_error_string):
                # This is needed to prevent an infinite loop 
                # as there would otherwise be infinite validation
                # on self.error()
                error_message = no_error_string
                return responce
            else:
                # We are in checking mode, we don't need to
                # firmly check for error on error.
                error_message = self.send_scpi_command(
                    command='SYSTem:ERRor?', _escape=True)
                # Check if the error message is blank.
                if (len(error_message) == 0):
                    # There was no responce?
                    warnings.warn("The error responce is blank. The "
                                  "power supply may not be responding.",
                                  RuntimeWarning, stacklevel=2)
                    print('No responce?')
                    # There is no point in continuing.
                    return responce
            # Check the error message.
            if (error_message == no_error_string):
                # There is no error.
                return responce
            else:
                # There is likely an error. Return it instead,
                warnings.warn("The power supply has an error from this "
                              "last command: `{cmd}`. \n"
                              "The error string is returned instead."
                              .format(cmd=command), 
                              RuntimeWarning, stacklevel=2)
                return error_message
        # The code should not reach here.
        raise RuntimeError('The error checking failed.')
        return None

    def _send_raw_scpi_command(self, bytestring):
        """ This function sends a remote command to the power supply
        for it to execute. No internet checks are done. This is 
        mostly a wrapper for the serial package. Moreover, the
        input and outputs are not formatted and are instead raw
        for and from serial.
        """
        # Load the serial connection information.
        port = self._serial_port
        baudrate = self._serial_baudrate
        parity = self._serial_parity
        data = self._serial_data
        start_bits = self._serial_start
        end_bits = self._serial_end
        timeout = self._serial_timeout

        # Load up the serial connection.
        with serial.Serial(
            port=port, baudrate=baudrate, bytesize=data,
            parity=parity, stopbits=end_bits, timeout=timeout) as ser:
            # Sending the command.
            ser.write(bytestring)
            # Read the responce, if any.
            if (timeout is None):
                # There is no timeout, the script will hang forever
                # if nothing is received. Using the default timeout
                # value.
                _old_timeout = copy.deepcopy(self._serial_timeout)
                ser.timeout = DEFAULT_TIMEOUT
                # Read the responce.
                responce = ser.readline()
                # Restore the old timeout value.
                ser.timeout = _old_timeout
            else:
                # There is a timeout, so just read the line.
                responce = ser.readline()

        # All done. Output the responce.
        return responce

    # Aliases.
    command = send = write = send_scpi_command
    _raw = _send_raw = _send_raw_scpi_command
    
    # Internal consistency function for the voltage property 
    # interfaces.
    def _generate_apply_command(self, output, voltage, current,
                                request=False):
        """ This is just a wrapper function to spit out a string
        that is a APPLy valid command for the function used. This 
        is only used for the variable interfaces and should not 
        be used otherwise.
        """
        ## Type check and validate.
        # Instrument type checking.
        output = str(output).upper()
        if (output in ('P6V','P25V','N25V')):
            # A valid instrument type.
            pass
        else:
            raise ValueError("The output specified is `{out}`, it must be "
                             "one the the following: 'P6V', 'P25V', 'N25V'"
                             .format(out=output))
        # The voltages and currents should be string represented. 
        # Also, if the parameter 'DEF', 'MIN', or 'MAX' is used, that
        # should be passed through instead.
        # Voltage
        if ((str(voltage).upper() in ('','DEF','MIN','MAX')) or 
            (voltage is None)):
            # Begin to convert.
            voltage = '' if (voltage is None) else voltage
            voltage_str = str(voltage).upper()
        else:
            voltage_str = '{:6f}'.format(float(voltage))
        # Current
        if ((str(current).upper() in ('','DEF','MIN','MAX')) or 
            (current is None)):
            # Begin to convert.
            current = '' if (current is None) else current
            current_str = str(current).upper()
        else:
            current_str = '{:6f}'.format(float(current))

        # Compile the command itself. If the user wants a request 
        # form, then compile that instead.
        if (request):
            # This is a request apply command.
            apply_command = ('APPLy? {out}'.format(out=output))
        else:
            apply_command = ('APPLy {out},{volt},{curr}'
                             .format(out=output, 
                                     volt=voltage_str, curr=current_str))
        # All done.
        return apply_command

def _ravel_dictionary(dictionary, conflict):
    """ This function unravels a dictionary, un-nesting
    nested dictionaries into a single dictionary. If
    conflicts arise, then the conflict rule is used.
    
    The keys of dictionary entries that have dictionary
    values are discarded.
    
    Parameters
    ----------
    dictionary : dictionary
        The dictionary to be unraveled.
    conflict : string
        The conflict rule. It may be one of these:
        
        * 'raise'
            If a conflict is detected, a 
            sparrowcore.DataError will be raised.
        * 'superior'
            If there is a conflict, the least 
            nested dictionary takes precedence. Equal
            levels will prioritize via alphabetical. 
        * 'inferior'
            If there is a conflict, the most
            nested dictionary takes precedence. Equal
            levels will prioritize via anti-alphabetical.
        
    Returns
    -------
    raveled_dictionary : dictionary
        The unraveled dictionary. Conflicts were replaced
        using the conflict rule.
    """
    # Reaffirm that this is a dictionary.
    if (not isinstance(dictionary, dict)):
        dictionary = dict(dictionary)
    else:
        # All good.
        pass
    # Ensure the conflict is a valid conflict type.
    conflict = str(conflict).lower()
    if (conflict not in ('raise', 'superior', 'inferior')):
        raise RuntimeError("The conflict parameter must be one the "
                           "following: 'raise', 'superior', 'inferior'.")
        
    # The unraveled dictionary.
    raveled_dictionary = dict()
    # Sorted current dictionary. This sorting helps
    # with priorities prescribed by `conflict`.
    sorted_dictionary = dict(sorted(dictionary.items()))
    for keydex, itemdex in sorted_dictionary.items():
        # If this entry is a dictionary, then 
        # recursively go through it like a tree search.
        if (isinstance(itemdex, dict)):
            temp_dict = _ravel_dictionary(
                dictionary=itemdex, conflict=conflict)
        else:
            # It is a spare item, create a dictionary.
            temp_dict = {keydex:itemdex}
        # Combine the dictionary, but, first, check for
        # intersection conflicts.
        if (len(raveled_dictionary.keys() & temp_dict.keys()) != 0):
            # There are intersections. Handle them based 
            # on `conflict`.
            if (conflict == 'raise'):
                raise RuntimeError("There are conflicts in these two "
                                   "dictionaries: \n"
                                   "Temp : {temp} \n Ravel : {ravel}"
                                   .format(temp=temp_dict, 
                                           ravel=raveled_dictionary))
            elif (conflict == 'superior'):
                # Preserve the previous entries as they are
                # either higher up in the tree or are
                # ahead alphabetically.
                raveled_dictionary = {**temp_dict, **raveled_dictionary}
            elif (conflict == 'inferior'):
                # Preserve the new entires as they are
                # either lower in the tree or are behind
                # alphabetically.
                raveled_dictionary = {**raveled_dictionary, **temp_dict}
            else:
                # The code should not get here.
                raise RuntimeError("The input checking of conflict "
                                   "should have caught this.")
        else:
            # They can just be combined as normal. Taking superior
            # as the default.
            raveled_dictionary = {**temp_dict, **raveled_dictionary}
            
    # All done.
    return raveled_dictionary


