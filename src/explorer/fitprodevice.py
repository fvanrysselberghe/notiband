"""
    Models our fitpro band
"""
import asyncio
import datetime
import struct
import time

from bleak import BleakClient, BleakScanner


class FitProDevice:
    def __init__(self, device, logger=None) -> None:
        self.client = BleakClient(device)
        self.logger = logger

    async def connect(self):
        await self.client.connect()

    async def disconnect(self):
        await self.client.disconnect()

    async def initialize_device(self):
        if self.client is None:
            return

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(
            FitProDevice.CMD_GROUP_GENERAL, FitProDevice.CMD_INIT1, b'\x02'))

        await self.client.write_gatt_char(
            FitProDevice.WriteCharacteristic, self.createTimeMessage())
        time.sleep(0.2)

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(
            FitProDevice.CMD_GROUP_REQUEST_DATA, FitProDevice.CMD_INIT1, None))
        time.sleep(0.2)

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(
            FitProDevice.CMD_GROUP_REQUEST_DATA, FitProDevice.CMD_INIT2, None))
        time.sleep(0.2)

        await self.client.write_gatt_char(
            FitProDevice.WriteCharacteristic, self.createLanguageMessage())
        time.sleep(0.2)

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(
            FitProDevice.CMD_GROUP_GENERAL, FitProDevice.CMD_INIT3, FitProDevice.VALUE_ON))
        time.sleep(0.2)

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(
            FitProDevice.CMD_GROUP_REQUEST_DATA, FitProDevice.VALUE_ON, None))
        time.sleep(0.2)

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(
            self.CMD_GROUP_REQUEST_DATA, b'\x0f', None))
        time.sleep(0.2)

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(
            FitProDevice.CMD_GROUP_REQUEST_DATA, FitProDevice.CMD_GET_HW_INFO, None))
        time.sleep(0.2)

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(
            FitProDevice.CMD_GROUP_BAND_INFO, FitProDevice.CMD_RX_BAND_INFO, None))
        time.sleep(0.2)

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(FitProDevice.CMD_GROUP_GENERAL, FitProDevice.CMD_NOTIFICATIONS_ENABLE, b'\x01'))

    async def sendNotification(self, message):
        icon = b'\x01'

        payload = bytearray()
        payload += icon
        payload += b'\x00'
        payload += b'\x00'

        payload += message.encode()

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(FitProDevice.CMD_GROUP_GENERAL, FitProDevice.CMD_NOTIFICATION_MESSAGE, payload))

    async def sendCallNotification(self, message):

        payload = bytearray()
        payload += b'\x01'
        payload += b'\x00'

        payload += message.encode()

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(FitProDevice.CMD_GROUP_GENERAL, FitProDevice.CMD_NOTIFICATION_CALL, payload))

    async def sendLongNotify(self):
        baseMessage = b'\xCD\x00\x14\x12\x01\x11\x00\x0F\x01\x00\x30\x30\x30\x30\x30\x30\x30\x30\x30\x30'

        # debug
        self.debugPrintArray(baseMessage)

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, baseMessage)
        time.sleep(0.1)

        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, b'\x30\x30\x30')

    async def stopLongNotify(self):
        await self.client.write_gatt_char(FitProDevice.WriteCharacteristic, self.createMessage(FitProDevice.CMD_GROUP_GENERAL, FitProDevice.CMD_NOTIFICATION_CALL, FitProDevice.VALUE_OFF))

    def createTimeMessage(self):
        now = datetime.datetime.now()

        currentDate = now.date()
        currentTime = now.time()

        encodedTimeValue = (currentDate.year - 2000) << 26 | \
            currentDate.month << 22 | \
            currentDate.day << 17 | \
            currentTime.hour << 12 | \
            currentTime.minute << 6 | \
            currentTime.second

        self.debugPrintArray(struct.pack('>i', encodedTimeValue))

        return self.createMessage(FitProDevice.CMD_GROUP_GENERAL, FitProDevice.CMD_SET_DATE_TIME,
                                  struct.pack('>i', encodedTimeValue))

    def createLanguageMessage(self):
        return self.createMessage(
            FitProDevice.CMD_GROUP_GENERAL, FitProDevice.CMD_SET_LANGUAGE, FitProDevice.LANG_NETHERLANDS)

    def createMessage(self, command_group, operationCode, payload):
        payloadSize = 0
        if payload is not None:
            payloadSize = len(payload)

        bytes = FitProDevice.MESSAGE_HEADER.copy()

        bytes[2] = (len(FitProDevice.MESSAGE_HEADER) - 3) + \
            payloadSize  # length field minus the first three bytes
        bytes[3] = command_group[0]  # assume single byte
        bytes[5] = operationCode[0]
        bytes[7] = payloadSize

        if payload is not None:
            bytes += payload

        # debug
        self.debugPrintArray(bytes)

        return bytes

    def debugPrintArray(self, bytePackage):
        if self.logger is not None:
            self.logger.info(bytePackage)

    WriteCharacteristic = "6e400002-b5a3-f393-e0a9-e50e24dcca9d"

    # Header
    MESSAGE_HEADER = bytearray(b'\xCD\x00\x00\x00\x01\x00\x00\x00')

    # Command Groups
    CMD_GROUP_GENERAL = b'\x12'
    CMD_GROUP_BAND_INFO = b'\x20'
    CMD_GROUP_RECEIVE_BUTTON_DATA = b'\x1c'
    CMD_GROUP_RECEIVE_SPORTS_DATA = b'\x15'
    CMD_GROUP_HEARTRATE_SETTINGS = b'\x16'
    CMD_GROUP_REQUEST_DATA = b'\x1a'
    CMD_GROUP_BIND = b'\x14'
    CMD_GROUP_RESET = b'\x1d'

    # Command Values for CMD_GROUP_GENERAL
    CMD_FIND_BAND = b'\x0c'
    CMD_SET_DATE_TIME = b'\x01'
    CMD_SET_LANGUAGE = b'\x15'
    CMD_NOTIFICATION_MESSAGE = b'\x12'
    CMD_NOTIFICATION_CALL = b'\x11'
    CMD_WEATHER = b'\x20'
    CMD_CAMERA = b'\x0c'
    CMD_HEART_RATE_MEASUREMENT = b'\x18'  # on/off
    CMD_DND = b'\x14'
    CMD_INIT1 = b'\x0a'
    CMD_INIT2 = b'\x0c'
    CMD_INIT3 = b'\xff'

    CMD_SET_SLEEP_TIMES = b'\x0F'
    CMD_ALARM = b'\x02'
    CMD_SET_ARM = b'\x06'
    CMD_GET_HR = b'\x0d'  # 0/1
    CMD_GET_PRESS = b'\x0e'  # 0/1

    CMD_NOTIFICATIONS_ENABLE = b'\x07'
    CMD_SET_LONG_SIT_REMINDER = b'\x05'

    CMD_SET_DISPLAY_ON_LIFT = b'\x09'
    CMD_SET_STEP_GOAL = b'\x03'
    CMD_SET_USER_DATA = b'\x04'
    CMD_SET_DEVICE_VIBRATIONS = b'\x08'

    # Command values for CMD_GROUP_BAND_INFO
    CMD_RX_BAND_INFO = b'\x02'

    # Command values for CMD_GROUP_REQUEST_DATA
    CMD_GET_STEPS_TARGET = b'\x02'
    CMD_GET_HW_INFO = b'\x10'
    CMD_GET_AUTO_HR = b'\x08'
    CMD_GET_CONTACTS = b'\x0d'

    # Values
    LANG_ENGLISH = b'\x01'
    LANG_GERMAN = b'\x05'
    LANG_SPANISH = b'\x06'
    LANG_FRENCH = b'\x07'
    LANG_NETHERLANDS = b'\x0a'

    VALUE_ON = b'\x01'
    VALUE_OFF = b'\x00'
    # VALUE_SET_NOTIFICATIONS_ENABLE_ON = new byte[]{\x1, \x1, \x1, \x1, \x1, \x1, \x1, \x1, \x1, \x1, \x1};
    # VALUE_SET_NOTIFICATIONS_ENABLE_OFF = new byte[]{\x0, \x0, \x0, \x0, \x0, \x0, \x0, \x0, \x0, \x0, \x0};
    # VALUE_SET_LONG_SIT_REMINDER_ON = new byte[]{\x0, \x1, \x0, b'\x96};
    # VALUE_SET_LONG_SIT_REMINDER_OFF = new byte[]{\x0, \x0, \x0, b'\x96, \x4, \x8, \x16, \x7f};
