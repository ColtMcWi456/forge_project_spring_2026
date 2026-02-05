class ArduinoRobot:
    """
    Handles:
    - Connecting to Arduino
    - Sending commands to Arduino
    - Optional: generating Arduino code
    """

    def __init__(self, port, baudrate=9600):
        self.port = port
        self.baudrate = baudrate
        self.connection = None

    def connect(self):
        """Connect to Arduino over serial."""
        pass

    def send_command(self, command):
        """
        Send a single command.

        Example command:
            ("F", 10)
            ("R", 90)
        """
        pass

    def send_commands(self, commands):
        """Send full list of commands."""
        pass

    def close(self):
        """Close Arduino connection safely."""
        pass