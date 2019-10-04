from rdt.base import *
import random


class SenderRdt20(Sender):
    last_packet = ""

    def send_data(self, data):
        self.last_packet = data
        text_data = data.encode()
        packet = bytearray(len(text_data) + 1)
        sum = 0
        for byte in text_data:
            sum += byte
        packet[0] = sum.to_bytes(8, byteorder="little")[0]
        packet[1:len(text_data) + 1] = text_data
        self.channel.send_to_receiver(packet)

    def receive_response(self, response):
        if response == b"ACK":
            print("[ACK] Packet went well")
        elif response == b"NAK":
            print("[NAK] Need to send the last packet again")
            self.send_data(self.last_packet)
        else:
            print("[Error] Bad response : need to send the last packet again")
            self.send_data(self.last_packet)


class ChannelRdt20(Channel):

    def send_to_receiver(self, data):
        # change data randomly
        if random.randint(0, 10) == 0:
            data_array = bytearray(data)
            data_array[random.randint(0, len(data_array)-1)] += 1
            data = data_array
        super().send_to_receiver(data)

    def send_to_sender(self, response):
        # change data randomly
        if random.randint(0, 10) == 0:
            response_array = bytearray(response)
            response_array[random.randint(0, len(response_array)-1)] += 1
            response = response_array
        super().send_to_sender(response)


class ReceiverRdt20(Receiver):
    def receive_data(self, data):
        check_sum = data[0]
        text_data = data[1:]
        sum = 0
        for byte in text_data:
            sum += byte
        if sum.to_bytes(8, byteorder="little")[0] == check_sum:
            super().receive_data(text_data)
            self.send_response(b"ACK")

        else:
            self.send_response(b"NAK")

    def send_response(self, response):
        super().send_response(response)


def main():
    sim = Simulation(sender=SenderRdt20(), channel=ChannelRdt20(), receiver=ReceiverRdt20())
    sim.simulate()


if __name__ == "__main__":
    main()
