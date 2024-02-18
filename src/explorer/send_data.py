"""
    Send a package to a given BTE device and handle
"""

import argparse
import asyncio
import logging

from bleak import BleakClient, BleakScanner

logger = logging.getLogger(__name__)


async def main(args: argparse.Namespace):
    logger.info("Preparing to send...")

    device = await BleakScanner.find_device_by_address(
        args.address)
    if device is None:
        logger.error("Could not find device with address '%s'", args.address)
        return

    logger.info("connecting to device...")

    async with BleakClient(
        device,
    ) as client:
        logger.info("connected")

        await client.write_gatt_char(args.handle, bytes.fromhex(args.data))

        logger.info("disconnecting...")

    logger.info("disconnected")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    device_group = parser.add_mutually_exclusive_group(required=True)

    device_group.add_argument(
        "--address",
        metavar="<address>",
        help="the address of the bluetooth device to connect to",
    )

    parser.add_argument(
        "--handle",
        metavar="<handle>",
        help="handle to write to"
    )

    parser.add_argument(
        "--data",
        metavar="<data>",
        help="data in a hexadecimal string to write"
    )

    args = parser.parse_args()

    log_level = logging.INFO
    logging.basicConfig(
        level=log_level,
        format="%(asctime)-15s %(name)-8s %(levelname)s: %(message)s",
    )

    asyncio.run(main(args))
