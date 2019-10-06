from rdt.base import *
from rdt.rdt20 import ChannelRdt20


class SenderRdt22(Sender):
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
        byte_sum = 0
        check_sum = response[4]
        for byte in response[0:4]:
            byte_sum += byte
        if byte_sum.to_bytes(8, byteorder='little')[0] != check_sum:
            print('[Error] Bad response checksum : need to send the last packet again: ' + self.last_packet)
            self.send_data(self.last_packet, resend=True)
            return

        print("[Sender] received response: "+str(response)+", checksum: "+str(check_sum)+", bytesum: "+str(byte_sum))

        if b"ACK" in response:
            ack_sequence_nmb = response[3]
            if ack_sequence_nmb == self.sequence_nmb - 1:
                print("[Duplicated ACK] Need to send the last packet again: " + self.last_packet +
                      ", ack sequence nmb: " + str(ack_sequence_nmb))
                self.send_data(self.last_packet, resend=True)
            elif ack_sequence_nmb == self.sequence_nmb:
                print("[ACK] Packet went well: " + self.last_packet + " ack sequence nmb: " + str(ack_sequence_nmb))
                self.sequence_nmb = ack_sequence_nmb + 1
                self.msg_lock.release()
            else:
                sys.stderr.write("[Error] Packet should not be THAT late, sequence nmb: " + str(self.sequence_nmb) +
                                 ", ack sequence nmb: " + str(ack_sequence_nmb))

        else:
            print("[Error] Bad response : need to send the last packet again ")
            self.send_data(self.last_packet, resend=True)


class ReceiverRdt22(Receiver):
    sequence_number = 0

    def receive_data(self, data):
        check_sum = data[0]
        sequence_nmb = data[1]
        text_data = data[2:]
        data_byte_sum = 0
        response = bytearray(5)
        for data_byte in text_data:
            data_byte_sum += data_byte
        data_byte_sum += sequence_nmb
        if data_byte_sum.to_bytes(8, byteorder="little")[0] == check_sum:
            if self.sequence_number != sequence_nmb:
                print("Receive packet: " + str(sequence_nmb) + " with last packet: " + str(self.sequence_number))
                self.sequence_number = sequence_nmb
                super().receive_data(text_data)
            else:
                print("Received duplicated data on receiver end: " + str(self.sequence_number) + ", packet: " + str(
                    sequence_nmb))
            response[0:2] = b"ACK"
            response[3] = self.sequence_number.to_bytes(8, byteorder='little')[0]
            response_byte_sum = 0
            for response_byte in response[0:4]:
                response_byte_sum += response_byte
            response[4] = response_byte_sum.to_bytes(8, byteorder='little')[0]
            self.send_response(response)

        else:
            response[0:2] = b"ACK"
            response[3] = self.sequence_number.to_bytes(8, byteorder='little')[0]
            response_byte_sum = 0
            for response_byte in response[0:4]:
                response_byte_sum += response_byte
            response[4] = response_byte_sum.to_bytes(8, byteorder='little')[0]
            self.send_response(response)

    def send_response(self, response):
        super().send_response(response)


def main():
    sim = Simulation(sender=SenderRdt22(), channel=ChannelRdt20(), receiver=ReceiverRdt22())
    sim.simulate()


if __name__ == "__main__":
    main()
