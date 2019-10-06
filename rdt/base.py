import time
import sys
import threading

class Receiver:
    channel = None
    received_data_buffer = []

    def receive_data(self, data):
        self.received_data_buffer.append(data.decode())
        print("Received packet from: " + data.decode())

    def send_response(self, response):
        self.channel.send_response(response)


class Sender:
    channel = None

    def send_data(self, data):
        self.channel.send_msg(data.encode())

    def receive_response(self, response):
        pass


class Channel:
    delay = 0.1
    sender = None
    receiver = None
    threads_buffer = []
    data_exchanged = 0

    def send_msg(self, data):
        self.data_exchanged += len(data)
        t = threading.Thread(target=self.sent_msg_to_receiver, args=(data,), daemon=True)
        t.start()
        self.threads_buffer.append(t)

    def sent_msg_to_receiver(self, data):
        time.sleep(self.delay)
        self.receiver.receive_data(data)

    def send_response(self, response):
        self.data_exchanged += len(response)
        t = threading.Thread(target=self.sent_response_sender, args=(response,), daemon=True)
        t.start()
        self.threads_buffer.append(t)

    def sent_response_sender(self, response):
        time.sleep(self.delay)
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
        start = time.time()
        for i in range(self.n):
            self.sender.send_data("Packet " + str(i+1))

        for t in self.channel.threads_buffer:
            t.join()
        print("Time: "+str(time.time()-start))
        print(self.receiver.received_data_buffer)
        print("Data exchanged: "+str(self.channel.data_exchanged))
        if len(self.receiver.received_data_buffer) != 100:
            sys.stderr.write("[Error] Not all data sent: "+str(len(self.receiver.received_data_buffer))+"\n")
