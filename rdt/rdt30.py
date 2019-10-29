from rdt.base import *
import random


class SenderRdt30(Sender):
    last_packet = ""
    current_sequence_nmb = 1
    timeout = 0.3
    msg_lock = threading.Lock()
    timeout_threads = []

    def send_data(self, data, resend=False):
        if not resend:
            self.msg_lock.acquire()
        self.last_packet = data
        text_data = data.encode()
        packet = bytearray(len(text_data) + 2)
        packet[1] = self.current_sequence_nmb.to_bytes(8, byteorder='little')[0]
        check_sum = 0
        for byte in text_data:
            check_sum += byte
        check_sum += packet[1]
        packet[0] = check_sum.to_bytes(8, byteorder="little")[0]
        packet[2:len(text_data) + 2] = text_data
        self.channel.send_msg(packet)
        t = threading.Thread(target=self.timeout_resend, args=(packet,), daemon=True)
        t.start()
        self.timeout_threads.append(t)

    def timeout_resend(self, packet):
        time.sleep(self.timeout)
        if self.current_sequence_nmb == packet[1]:
            print("[Error] Timeout, need to sent the last packet again: " + self.last_packet)
            self.send_data(self.last_packet, resend=True)

    def receive_response(self, response):
        check_sum = 0
        for byte in response[0:4]:
            check_sum += byte
        if check_sum.to_bytes(8, byteorder='little')[0] != response[4]:
            print("[Error] Bad response checksum : need to send the last packet again: " + self.last_packet)
            self.send_data(self.last_packet, resend=True)
            return

        if b"ACK" in response:
            ack_sequence_nmb = response[3]
            if ack_sequence_nmb == self.current_sequence_nmb - 1:
                print("[Duplicated ACK] Need to send the last packet again: " + self.last_packet+" ack: "+str(ack_sequence_nmb))
                self.send_data(self.last_packet, resend=True)
            elif ack_sequence_nmb == self.current_sequence_nmb:
                print("[ACK] Packet went well: " + self.last_packet + " ack sequence nmb: " + str(ack_sequence_nmb))
                self.current_sequence_nmb = ack_sequence_nmb + 1
                self.msg_lock.release()
            else:
                sys.stderr.write("[Error] Packet should not be THAT late, sequence nmb: " + str(self.current_sequence_nmb) +
                                 ", ack sequence nmb: " + str(ack_sequence_nmb))

        else:
            print("[Error] Bad response : need to send the last packet again")
            self.send_data(self.last_packet, resend=True)


class ReceiverRdt30(Receiver):
    last_success_seq_number = 0

    def receive_data(self, data):
        check_sum = data[0]
        sequence_nmb = data[1]
        text_data = data[2:]
        data_byte_sum = 0
        response = bytearray(5)
        for byte in text_data:
            data_byte_sum += byte
        data_byte_sum += sequence_nmb
        if data_byte_sum.to_bytes(8, byteorder="little")[0] == check_sum:
            if self.last_success_seq_number != sequence_nmb:
                print("Receive packet: " + str(sequence_nmb) +" with last packet: " + str(self.last_success_seq_number))
                self.last_success_seq_number = sequence_nmb
                super().receive_data(text_data)
            else:
                print("[Duplicated] Receive packet: " + str(sequence_nmb) + " with last packet: " + str(self.last_success_seq_number))

            response[0:2] = b"ACK"

            response[3] = self.last_success_seq_number.to_bytes(8, byteorder='little')[0]
            response_byte_sum = 0
            for response_byte in response[0:4]:
                response_byte_sum += response_byte
            response[4] = response_byte_sum.to_bytes(8, byteorder='little')[0]
            self.send_response(response)

        else:
            print(
                "[Error] Bad checksum, resending ACK for: "+str(self.last_success_seq_number))
            response[0:2] = b"ACK"
            response[3] = self.last_success_seq_number.to_bytes(8, byteorder='little')[0]
            response_byte_sum = 0
            for byte in response[0:4]:
                response_byte_sum += byte
            response[4] = response_byte_sum.to_bytes(8, byteorder='little')[0]
            self.send_response(response)

    def send_response(self, response):
        super().send_response(response)


class ChannelRdt30(Channel):

    def send_msg(self, data):
        # change data randomly
        if random.randint(0, 10) == 0:
            print("[Msg Corruption] "+str(data[1]))
            data_array = bytearray(data)
            data_array[random.randint(0, len(data_array) - 1)] += 1
            data = data_array
        if random.randint(0, 10) == 0:
            print("[Msg Loss] "+str(data[1]))
            self.data_exchanged += len(data)
            return
        super().send_msg(data)

    def send_response(self, response):
        # change data randomly
        if random.randint(0, 10) == 0:

            response_array = bytearray(response)
            response_array[random.randint(0, len(response_array) - 1)] += 1
            response = response_array
        if random.randint(0, 10) == 0:

            self.data_exchanged += len(response)
            return
        super().send_response(response)


class SimulationRdt30(Simulation):

    def simulate(self):
        start = time.time()
        for i in range(self.n):
            self.sender.send_data("Packet " + str(i + 1))
        for t in self.channel.threads_buffer:
            t.join()
        for t in self.sender.timeout_threads:
            t.join()
        print("Time: " + str(time.time() - start))
        print(self.receiver.received_data_buffer)
        print("Data exchanged: "+str(self.channel.data_exchanged))
        if len(self.receiver.received_data_buffer) != 100:
            sys.stderr.write("[Error] Not all data sent: " + str(len(self.receiver.received_data_buffer)) + "\n")


def main():
    sim = SimulationRdt30(sender=SenderRdt30(), channel=Channel(), receiver=ReceiverRdt30())
    sim.simulate()


if __name__ == "__main__":
    main()
