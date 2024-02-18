"""
    Connector application.
    Takes care of the handshake, and sends a message
"""

import argparse
import asyncio
import logging
import time
import fitprodevice

from bleak import BleakClient, BleakScanner

logger = logging.getLogger(__name__)


async def main():
    logger.setLevel(level=logging.INFO)
    logger.info("Preparing to send...")

    device = None
    while device is None:
        device = await BleakScanner.find_device_by_address('C0:00:00:00:0E:A7')

    fitpro = fitprodevice.FitProDevice(device, logger)

    logger.info("Connecting...")
    await fitpro.connect()

    logger.info("Initializing...")
    await fitpro.initialize_device()

    logger.info("Message -> PAS OP")
    await fitpro.sendNotification('Pas op')
    time.sleep(2)

    logger.info("Long Notify Test")
    await fitpro.sendCallNotification('PAS OP')
    time.sleep(10)

    logger.info("Stop calling")
    await fitpro.stopLongNotify()

    logger.info("Disconnecting...")
    await fitpro.disconnect()

    logger.info("disconnected")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s")

    asyncio.run(main())
