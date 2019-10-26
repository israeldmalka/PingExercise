import socket
import argparse

class Server:

    def __init__(self, arguments):
        # create the server
        
        self.protocol = arguments.protocol
        self.port = arguments.port
        self.packet_size = arguments.packetsize

        self.create_socket()

        server_address = ('', self.port)
        self.socket.bind(server_address)
    
    def create_socket(self):
        # create a socket from the server to the client
        
        socket_family = socket.AF_INET
                
        if self.protocol == 'TCP':
            socket_type = socket.SOCK_STREAM
        elif self.protocol == 'UDP':
            socket_type = socket.SOCK_DGRAM
        else:
            raise ValueException('Illegal Protocol {}, must be either TCP or UDP'.format(self.protocol))
        
        protocol_number = socket.getprotobyname(self.protocol)

        self.socket = socket.socket(socket_family, socket_type, protocol_number)

    def tcp_start(self):
        # start receiving and resending packages using TCP protocol

        self.socket.listen(5)
        
        while True:

            clt, adr = self.socket.accept()

            print(f'Client {adr} Connected')

            while True:
                
                data = clt.recv(self.packet_size)

                if not data:

                    print(f'Client {adr} Disconnected')

                    break
                
                print(f'{len(data)} bytes received through TCP protocol') 
                
                clt.send(data)
                    
    def udp_start(self):
        # start receiving and resending packages using UDP protocol
        
        while True:

            data, adr = self.socket.recvfrom(self.packet_size)

            if not data:
                
                continue
                
            print(f'{len(data)} bytes received through UDP protocol')
                
            self.socket.sendto(data, adr)


    def start(self):
        # listen to client requests

        print('Server started')

        if self.protocol == 'TCP':

            self.tcp_start()

        if self.protocol == 'UDP':

            self.udp_start()


    def close(self):
        # close the connection
        self.socket.close()

        print('Server closed')


def validate_arguments(arguments):
    supported_protocols = ['TCP', 'UDP']

    # validate arguments values

    if not arguments.protocol in supported_protocols:
        raise ValueError('Illegal Protocol {}, must be either TCP or UDP'.format(arguments.protocol))

    if arguments.port < 1 or arguments.port > 65535:
        raise ValueError('Illegal Port number {}, must be between 1 and 65535'.format(arguments.port))

    if arguments.timeout < 1:
        raise ValueError('Illegal Timeout value {}, must be a positive integer'.format(arguments.timeout))

    if arguments.packetsize < 1:
        raise ValueError('Illegal Packet size {}, must be a positive integer'.format(arguments.packetsize))
        
def handle_arguments():
    parser = argparse.ArgumentParser()

    # basic arguments : protocol and port
    
    parser.add_argument('--protocol', help='the protocol (TCP or UDP) used in the connection (default: TCP)', type=str, default='TCP')
    parser.add_argument('--port', help='the port used in the connection (default: 1024)', type=int, default=1024)

    # optional arguments : timeout and packet size

    parser.add_argument('-t','--timeout', help='time to wait for a response in seconds (default: 3)', type=int, default=3)
    parser.add_argument('-s','--packetsize', help='number of databytes to be sent (default: 64)', type=int, default=64)
    arguments = parser.parse_args()

    validate_arguments(arguments)

    return arguments
    

def main():
    arguments = handle_arguments()
    server = Server(arguments)
    try:
        server.start()
    finally:
        server.close()
    
if __name__ == '__main__':
    main()
