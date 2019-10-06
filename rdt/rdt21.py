from rdt.base import *
from rdt.rdt20 import ChannelRdt20


class SenderRdt21(Sender):
    last_packet = ""
    sequence_nmb = 1
    msg_lock = threading.Lock()

    def send_data(self, data, resend=False):
        if not resend:
            self.msg_lock.acquire()
        self.last_packet = data
        text_data = data.encode()
        packet = bytearray(len(text_data) + 2)
        packet[1] = self.sequence_nmb.to_bytes(8, byteorder='little')[0]
        check_sum = 0
        for byte in text_data:
            check_sum += byte
        check_sum += packet[1]
        packet[0] = check_sum.to_bytes(8, byteorder="little")[0]
        packet[2:len(text_data) + 2] = text_data
        self.channel.send_msg(packet)

    def receive_response(self, response):
        check_sum = 0
        for byte in response[0:2]:
            check_sum += byte
        if check_sum.to_bytes(8, byteorder='little')[0] != response[3]:
            print("[Error] Bad response checksum : need to send the last packet again: "+self.last_packet)
            self.send_data(self.last_packet, resend=True)
            return

        if b"ACK" in response:
            print("[ACK] Packet went well")
            self.sequence_nmb += 1
            self.msg_lock.release()

        elif b"NAK" in response:
            print("[NAK] Need to send packet again")
            self.send_data(self.last_packet, resend=True)
        else:
            print("[Error] Bad response : need to send the last packet again")
            self.send_data(self.last_packet, resend=True)


class ReceiverRdt21(Receiver):
    sequence_number = 0

    def receive_data(self, data):
        check_sum = data[0]
        sequence_nmb = data[1]
        text_data = data[2:]
        byte_sum = 0
        response = bytearray(4)
        for byte in text_data:
            byte_sum += byte
        byte_sum += sequence_nmb
        if byte_sum.to_bytes(8, byteorder="little")[0] == check_sum:
            if self.sequence_number != sequence_nmb:
                super().receive_data(text_data)

            self.sequence_number = sequence_nmb
            response[0:2] = b"ACK"
            byte_sum = 0
            for byte in response[0:2]:
                byte_sum += byte
            response[3] = byte_sum.to_bytes(8, byteorder='little')[0]
            self.send_response(response)

        else:
            response[0:2] = b"NAK"
            byte_sum = 0
            for byte in response[0:2]:
                byte_sum += byte
            response[3] = byte_sum.to_bytes(8, byteorder='little')[0]
            self.send_response(response)

    def send_response(self, response):
        super().send_response(response)


def main():
    sim = Simulation(sender=SenderRdt21(), channel=ChannelRdt20(), receiver=ReceiverRdt21())
    sim.simulate()


if __name__ == "__main__":
    main()
