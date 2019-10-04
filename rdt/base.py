

class Sender:
    channel = None

    def send_data(self, data):
        self.channel.send_to_receiver(data.encode())

    def receive_response(self, response):
        pass


class Receiver:
    channel = None
    received_data_buffer = []

    def receive_data(self, data):
        self.received_data_buffer.append(data.decode())
        print("Received packet from: "+data.decode())

    def send_response(self, response):
        self.channel.send_to_sender(response)


class Channel:
    sender = None
    receiver = None

    def send_to_receiver(self, data):
        self.receiver.receive_data(data)

    def send_to_sender(self, response):
        self.sender.receive_response(response)


class Simulation:
    n = 100

    def __init__(self, channel=Channel(), receiver=Receiver(), sender=Sender()):
        self.channel = channel
        self.receiver = receiver
        self.sender = sender

        self.channel.receiver = self.receiver
        self.channel.sender = self.sender
        self.sender.channel = self.channel
        self.receiver.channel = self.channel

    def simulate(self):
        for i in range(self.n):
            self.sender.send_data("Packet "+str(i))
        print(self.receiver.received_data_buffer)

