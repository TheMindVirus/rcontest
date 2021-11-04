import random, asyncio, sys, struct

class RCON:
    def __init__(self):
        self.host = "127.0.0.1"
        self.port = 25575
        self.pswd = "123456"
        
        self.reader = None
        self.writer = None
        self.timeout = 10

        self.LOGIN = 3 # 1
        self.COMMAND = 2
        self.RESPONSE = 0
        self.INVALID_AUTH = -1

        print("__//Minecraft RCON Test\\\\__")
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.connect())

    async def connect(self):
        try:
            print("Connecting to Host...", file = sys.stderr)
            self.reader, self.writer = await \
                asyncio.wait_for(asyncio.open_connection(self.host, self.port), self.timeout)
            _, msg = await self.exchange(self.LOGIN, self.pswd)
            sys.stdout.write("Connected")
            if msg:
                sys.stdout.write(": ")
                sys.stderr.write(msg)
            else:
                print()
        except Exception as error:
            print(error, file = sys.stderr)

    def command(self, command):
        try:
            message = self.loop.run_until_complete(self.exchange(self.COMMAND, command))
            print("Received:", message)
            return message
        except Exception as error:
            print(error, file = sys.stderr)
            return None

    async def exchange(self, request_type, message):
        request_id = random.randint(0, 65535)
        data = struct.pack("<ii", request_id, request_type) \
             + message.encode("utf8") + b"\x00\x00"
        packet = struct.pack("<i", len(data)) + data
        self.writer.write(packet)
        await self.writer.drain()
        available = struct.unpack("<i", (await self.reader.read(4)))[0]
        data = await self.reader.read(available)
        if not data.endswith(b"\x00\x00"):
            raise Exception("Invalid Data Received")
            return None
        request_type, request_id = struct.unpack("<ii", data[0:8])
        if request_type == self.INVALID_AUTH:
            raise Exception("Invalid Password Entered")
            return None
        message = data[8:-2].decode("utf8")
        return request_type, message

    def __del__(self):
        try:
            self.writer.close()
            self.writer = None
            self.reader = None
            print("Terminated", file = sys.stderr)
        except Exception as error:
            print(error, file = sys.stderr)

#t = 0
t = 18000
rcontest = RCON()
rcontest.command("time set " + str(t))
rcontest.__del__()
