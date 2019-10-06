from rdt.base import *
import random
import time
import threading

class SenderRdt20(Sender):
    last_packet = None
    msg_lock = threading.Lock()

    def send_data(self, data, resend=False):
        if not resend:
            self.msg_lock.acquire()
        self.last_packet = data
        text_data = data.encode()
        packet = bytearray(len(text_data) + 1)
        check_sum = 0
        for byte in text_data:
            check_sum += byte
        packet[0] = check_sum.to_bytes(8, byteorder="little")[0]
        packet[1:len(text_data) + 1] = text_data
        self.channel.send_msg(packet)

    def receive_response(self, response):
        if response == b"ACK":
            print("[ACK] Packet went well, sending next one!")
            self.msg_lock.release()
        elif response == b"NAK":
            print("[NAK] Need to send the last packet again")
            self.send_data(self.last_packet, resend=True)
        else:
            print("[Error] Bad response : need to send the last packet again")
            self.send_data(self.last_packet, resend=True)


class ChannelRdt20(Channel):

    def send_msg(self, data):
        # change data randomly
        if random.randint(0, 10) == 0:
            print("[Msg Corruption]")
            data_array = bytearray(data)
            data_array[random.randint(0, len(data_array) - 1)] += 1
            data = data_array
        super().send_msg(data)

    def send_response(self, response):
        # change data randomly
        if random.randint(0, 10) == 0:
            print("[Response Corruption]")
            response_array = bytearray(response)
            response_array[random.randint(0, len(response_array) - 1)] += 1
            response = response_array
        super().send_response(response)


class ReceiverRdt20(Receiver):
    def receive_data(self, data):
        check_sum = data[0]
        text_data = data[1:]
        byte_sum = 0
        for byte in text_data:
            byte_sum += byte
        if byte_sum.to_bytes(8, byteorder="little")[0] == check_sum:
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
