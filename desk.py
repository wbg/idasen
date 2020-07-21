# super simply python script that moves my ikea idasen desk
# this is a very crude version of the much better implementation by @rhyst that you can find here: https://github.com/rhyst/idasen-controller
# i took the idea and made it work on osx using the fabulous bleak library
import asyncio
import struct
import time
import argparse

from bleak import BleakClient

UUID_HEIGHT = '99fa0021-338a-1024-8a49-009c0215f78a'
UUID_COMMAND = '99fa0002-338a-1024-8a49-009c0215f78a'
COMMAND_UP = struct.pack("<H", 71)
COMMAND_DOWN = struct.pack("<H", 70)
COMMAND_STOP = struct.pack("<H", 255)

parser = argparse.ArgumentParser(description='Move Desk up and Down')
parser.add_argument('--stand-up-height', default=5900, help='sum the integers (default: find the max)')
parser.add_argument('--sit-down-height', default=1650, help='sum the integers (default: find the max)')
parser.add_argument('--position', default="stand")
parser.add_argument('--address', default="1900E99F-FD66-42C0-AD0C-29B9AB96E102")
args = parser.parse_args()

POSITION=args.position

STAND_UP_HEIGHT=args.stand_up_height
SIT_DOWN_HEIGHT=args.sit_down_height

ADDRESS = args.address

async def run(address, loop):
    async with BleakClient(address, loop=loop, timeout=1.0) as client:        
        await client.is_connected()
        stop_event = asyncio.Event()
        async def goUp():
            await client.write_gatt_char(UUID_COMMAND, COMMAND_UP);
        async def goDown():
            await client.write_gatt_char(UUID_COMMAND, COMMAND_DOWN);
        async def goStop():
            await client.write_gatt_char(UUID_COMMAND, COMMAND_STOP);
        def notification_handler(sender, data):
            height, speed = struct.unpack("<Hh", data)
            if POSITION == "stand":
                if height < STAND_UP_HEIGHT:
                    asyncio.ensure_future(goUp())
                else:
                    asyncio.ensure_future(goStop())
                    stop_event.set()
            else: 
                if height > SIT_DOWN_HEIGHT:
                    asyncio.ensure_future(goDown())
                else:
                    asyncio.ensure_future(goStop())
                    stop_event.set()
        await client.start_notify(UUID_HEIGHT, notification_handler)
        await client.write_gatt_char(UUID_COMMAND, COMMAND_UP)
        await stop_event.wait()
        await client.stop_notify(UUID_HEIGHT)
        await client.disconnect()


loop = asyncio.get_event_loop()
loop.run_until_complete(run(ADDRESS, loop))