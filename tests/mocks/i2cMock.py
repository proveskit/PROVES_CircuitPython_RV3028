from tests.stubs.i2c_device import I2C, I2CDevice


class MockI2C(I2C):
    def __init__(self):
        self.registers = [0x00] * 256  # 256 8 bit registers


class MockI2CDevice(I2CDevice):
    def __init__(self, i2c: MockI2C, address):
        self.i2c = i2c
        self.address = address
        self.current_register = None

    # Context manager methods
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def write(self, data):
        if len(data) == 1:
            # Setting current register for subsequent read
            self.current_register = data[0]
        elif len(data) > 1:
            # First byte is the register address
            register = data[0]
            # Write the data to consecutive registers
            self.i2c.registers[register : register + len(data[1:])] = data[1:]
            self.current_register = register  # Update current register

    def readinto(self, buffer):
        if self.current_register is None:
            raise RuntimeError("Register address not set before read")
        for i in range(len(buffer)):
            buffer[i] = self.i2c.registers[self.current_register + i]
        self.current_register += len(buffer)
