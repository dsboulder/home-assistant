from bluepy.btle import UUID, Peripheral
import struct
import binascii


class SomaBlind:
    def __init__(self, mac):
        self._mac = mac
        self.connect()

    def connect(self):
        self._peripheral = Peripheral(self._mac, "random")
        self._batt_service = self._peripheral.getServiceByUUID("0000180f-0000-1000-8000-00805f9b34fb")
        self._motor_service = self._peripheral.getServiceByUUID("00001861-b87f-490c-92cb-11ba5ea5167c")

    def disconnect(self):
        self._peripheral.disconnect()

    def get_position(self):
        motor = self._get_motor_characteristic()
        byt = motor.read() 
        return struct.unpack("B", byt)[0]

    def get_battery(self):
        batt = self._batt_service.getCharacteristics("00002a19-0000-1000-8000-00805f9b34fb")[0]
        byt = batt.read() 
        return struct.unpack("B", byt)[0]

    # 0 means open, 100 means closed
    def set_position(self, value):
        motor = self._get_motor_characteristic()
        byt = struct.pack('B', value)
        return motor.write(byt) 

    def close(self):
        return self.set_position(100)

    def open(self):
        return self.set_position(0)

    def _get_motor_characteristic(self):
        return self._motor_service.getCharacteristics("00001526-b87f-490c-92cb-11ba5ea5167c")[0]

