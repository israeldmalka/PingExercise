import socket
import argparse
import datetime
import enum
import re

class Protocol(enum.Enum):
    
    TCP = 'TCP'
    UDP = 'UDP'
    
    def __str__(self):
        return self.value
    
    def __int__(self):
        return socket.getprotobyname(self.value)

    def isvalid(name):
        return name in Protocol._member_names_

    def getprotocol(name):
        if Protocol.isvalid(name):
            return Protocol._value2member_map_[name]
        else:
            raise ValueError('Invalid Protocol Name', name)

# decorator to calculate duration in milliseconds
def calculate_time(function):
    
    def inner(*args, **kwargs): 
        before_time = datetime.datetime.now()
        retval = function(*args, **kwargs) 
        after_time = datetime.datetime.now()
        
        time_delta = after_time - before_time
        duration = time_delta.microseconds / 1000

        result = {'retval': retval, 'duration': duration}        
        return result

    return inner
    
class Client:
    
    """
        The client class represents the Ping client.

        It holds the connection data (ip_address, protocol and port),

        other configurations (packets_num, timeout and packet_size)

        and the connection socket.

    """

    def __init__(self, arguments):
        # create a client object

        self.ip_address = arguments.ip_address
        self.protocol = arguments.protocol
        self.port = arguments.port

        self.packets_num = arguments.count
        self.timeout = arguments.timeout
        self.packet_size = arguments.packetsize

        self.create_socket()


    def create_socket(self):
        # create a socket from the client to the server
        
        socket_family = socket.AF_INET
                
        if self.protocol == Protocol.TCP:
            socket_type = socket.SOCK_STREAM
        elif self.protocol == Protocol.UDP:
            socket_type = socket.SOCK_DGRAM
        
        protocol_number = int(self.protocol)

        self.socket = socket.socket(socket_family, socket_type, protocol_number)

        self.socket.settimeout(self.timeout)

    def connect(self):
        # connect to the server, not relevant for UDP protocol

        if self.protocol == Protocol.UDP:
            return
        
        server_address = (self.ip_address, self.port)
        self.socket.connect(server_address)
        print(f'Ping connected to {self.ip_address} at port {self.port} using {self.protocol}')


    @calculate_time
    def send_tcp_packet(self):

        packet_to_send = bytes(self.packet_size)

        self.socket.send(packet_to_send)
        
        data = self.socket.recv(self.packet_size)

        left_bytes = len(packet_to_send) - len(data)

        received_packet = data

        while left_bytes > 0 and len(data) > 0:
            
            data = self.socket.recv(self.packet_size)

            left_bytes = left_bytes - len(data)

            received_packet = received_packet + data

        return received_packet


    @calculate_time
    def send_udp_packet(self):

        packet_to_send = bytes(self.packet_size)

        server_address = (self.ip_address, self.port)

        self.socket.sendto(packet_to_send, server_address)

        (data, _) = self.socket.recvfrom(self.packet_size)

        return data

    def send_packets(self):
        # send packets to the server
        
        iteration = 0
        while iteration < self.packets_num:

            try:

                if self.protocol == Protocol.TCP:

                    result = self.send_tcp_packet()

                elif self.protocol == Protocol.UDP:

                    result = self.send_udp_packet()
                
                received_packet = result['retval']

                received_size = len(received_packet)

                duration = result['duration']
                
                print(f'{received_size} bytes from {self.ip_address}: seq={iteration} time={duration} ms')

            except Exception as error:

                print(f'Ping {iteration} failed: could not send or retrieve a packet from the server')

                print(error)

            iteration += 1

    def close(self):
        # close the connection        
        self.socket.close()

def validate_arguments(arguments):
    ip_regex = '\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}'

    # validate arguments values

    if not re.fullmatch(ip_regex, arguments.ip_address):
        raise ValueError('Illegal IP address {}'.format(arguments.ip_address))

    if Protocol.isvalid(arguments.protocol) == False:
        raise ValueError('Illegal Protocol {}, must be either TCP or UDP'.format(arguments.protocol))

    if arguments.port < 1 or arguments.port > 65535:
        raise ValueError('Illegal Port number {}, must be between 1 and 65535'.format(arguments.port))

    if arguments.timeout < 1:
        raise ValueError('Illegal Timeout value {}, must be a positive integer'.format(arguments.timeout))

    if arguments.packetsize < 1:
        raise ValueError('Illegal Packet size {}, must be a positive integer'.format(arguments.packetsize))
    
    if arguments.count < 1:
        raise ValueError('Illegal Count value {}, must be a positive integer'.format(arguments.count))

def handle_arguments():
    parser = argparse.ArgumentParser()

    # basic arguments : ip_address, protocol and port

    parser.add_argument('ip_address', help='the server ip address to ping', type=str)
    parser.add_argument('--protocol', help='the protocol (TCP or UDP) used in the connection (default: TCP)', type=str, default='TCP')
    parser.add_argument('--port', help='the port used in the connection (default: 1024)', type=int, default=1024)

    # optional arguments : count, timeout and packet size
    
    parser.add_argument('-c', '--count', help='number of packets to send (default: 3)', type=int, default=3)
    parser.add_argument('-t','--timeout', help='time to wait for a response in seconds (default: 3)', type=int, default=3)
    parser.add_argument('-s','--packetsize', help='number of databytes to be sent (default: 64)', type=int, default=64)
    arguments = parser.parse_args()

    validate_arguments(arguments)

    # translate the protocol name to a Protocol enum instance

    arguments.protocol = Protocol.getprotocol(arguments.protocol)

    return arguments

def main():
    arguments = handle_arguments()
    client = Client(arguments)
    client.connect()
    
    try:
        client.send_packets()
    finally:
        client.close()
    
if __name__ == '__main__':
    main()
