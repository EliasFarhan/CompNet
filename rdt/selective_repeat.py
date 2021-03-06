from rdt.base import *
from rdt.rdt30 import ChannelRdt30, SimulationRdt30
import threading


class SenderSr(Sender):
    n = 8
    ack_buffer = []
    packet_buffer = []
    pool_sema = threading.BoundedSemaphore(value=n)
    timeout = 0.5
    timeout_threads = []
    base = 1
    current_sequence_nmb = 0
    receive_response_lock = threading.Lock()

    def send_data(self, data, resend=False):
        if not resend:
            self.pool_sema.acquire()
            self.current_sequence_nmb += 1

        text_data = data.encode()
        packet = bytearray(len(text_data) + 2)
        packet[1] = self.current_sequence_nmb.to_bytes(8, byteorder='little')[0]
        check_sum = 0
        for byte in text_data:
            check_sum += byte
        check_sum += packet[1]
        packet[0] = check_sum.to_bytes(8, byteorder="little")[0]
        packet[2:len(text_data) + 2] = text_data
        self.packet_buffer.append(packet)
        self.channel.send_msg(packet)
        t = threading.Thread(target=self.timeout_resend, args=(packet,), daemon=True)
        t.start()
        self.timeout_threads.append(t)

    def timeout_resend(self, packet):
        time.sleep(self.timeout)

        if self.base <= packet[1] and packet[1] not in self.ack_buffer:
            print("[Error] Timeout, need to sent the last packet again, Packet: "+str(packet[1]))
            self.channel.send_msg(packet)
            t = threading.Thread(target=self.timeout_resend, args=(packet,), daemon=True)
            t.start()
            self.timeout_threads.append(t)

    def receive_response(self, response):
        check_sum = response[4]
        byte_sum = 0
        for byte in response[0:4]:
            byte_sum += byte
        if byte_sum.to_bytes(8, byteorder='little')[0] != check_sum:
            return
        self.receive_response_lock.acquire()
        if b"ACK" in response:
            ack_sequence_nmb = response[3]
            if ack_sequence_nmb == self.base - 1:
                print("[Duplicated ACK] Need to send the base packet again, ack: " + str(
                    ack_sequence_nmb))
                if len(self.packet_buffer) > 0:
                    self.channel.send_msg(self.packet_buffer[0])
                    t = threading.Thread(target=self.timeout_resend, args=(self.packet_buffer[0],), daemon=True)
                    t.start()
                    self.timeout_threads.append(t)
            elif self.base + self.n > ack_sequence_nmb >= self.base:
                print("[ACK] Packet went well, ack sequence nmb: " + str(ack_sequence_nmb))
                self.ack_buffer.append(ack_sequence_nmb)
                if ack_sequence_nmb == self.base:
                    self.pool_sema.release()
                    # calculate new base
                    new_base = self.base
                    for i in range(self.n+1):
                        if self.base + i not in self.ack_buffer:
                            for x in range(i):
                                self.packet_buffer.pop(0)
                            self.base = new_base + i
                            self.ack_buffer[:] = [ack for ack in self.ack_buffer if ack > self.base]
                            break

        self.receive_response_lock.release()


class ReceiverSr(Receiver):
    n = 8
    receiver_base = 0
    msg_buffer = [None for i in range(n)]
    receiver_lock = threading.Lock()

    def receive_data(self, data):
        self.receiver_lock.acquire()
        check_sum = data[0]
        sequence_nmb = data[1]
        text_data = data[2:]
        data_byte_sum = 0
        response = bytearray(5)
        for byte in text_data:
            data_byte_sum += byte
        data_byte_sum += sequence_nmb
        if data_byte_sum.to_bytes(8, byteorder="little")[0] == check_sum:
            if self.receiver_base == sequence_nmb - 1:

                self.receiver_base = sequence_nmb
                super().receive_data(text_data)
                delta_base = 0
                for i in range(self.n):
                    if self.msg_buffer[i] is not None:
                        super().receive_data(self.msg_buffer[i])
                        delta_base += 1
                    else:
                        break
                self.receiver_base += delta_base
                for i in range(delta_base+1):
                    self.msg_buffer.pop(0)
                    self.msg_buffer.append(None)
            elif self.receiver_base < sequence_nmb - 1:
                self.msg_buffer[sequence_nmb-self.receiver_base-2] = text_data

            response[0:2] = b"ACK"
            response[3] = sequence_nmb.to_bytes(8, byteorder='little')[0]
            response_byte_sum = 0
            for response_byte in response[0:4]:
                response_byte_sum += response_byte
            response[4] = response_byte_sum.to_bytes(8, byteorder='little')[0]
            self.send_response(response)
        else:
            sys.stderr.write(
                "[Error] Bad checksum, resending ACK for: " + str(self.receiver_base) + "\n")
            response[0:2] = b"ACK"
            response[3] = self.receiver_base.to_bytes(8, byteorder='little')[0]
            response_byte_sum = 0
            for byte in response[0:4]:
                response_byte_sum += byte
            response[4] = response_byte_sum.to_bytes(8, byteorder='little')[0]
            self.send_response(response)
        self.receiver_lock.release()

    def send_response(self, response):
        super().send_response(response)


def main():
    sim = SimulationRdt30(sender=SenderSr(), receiver=ReceiverSr(), channel=ChannelRdt30())
    sim.simulate()


if __name__ == "__main__":
    main()
