import socket
import argparse
import sys
import random 
import struct 

# ensure port number is a positive integerless than 65536
def port_number(value):
    try:
        ivalue = int(value)
        if ivalue < 1 or ivalue > 65536:
            raise argparse.ArgumentTypeError(f"ERR - arg 1")
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError(f"ERR - arg 1")

def packet_loss(value):
    try:
        ivalue = float(value)
        if ivalue < 0 or ivalue > 100:
            raise argparse.ArgumentTypeError(f"ERR - arg 2")
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError(f"ERR - arg 2")

# parse command line arguments
parser = argparse.ArgumentParser(description='UDP PINGServer')
parser.add_argument('server_port', type=port_number, help='Port that will listen on for incoming pings for clients')
parser.add_argument('packet_loss', type=packet_loss, help='percentage of packet drop')
args = parser.parse_args()

server_ip = '0.0.0.0'
server_port = args.server_port

# if port number is already being taken by another active socket 
try:
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSock.bind((server_ip, server_port))
except socket.error as e: 
    print("ERR - cannot create PINGServer socket using port number {server_port}")
    sys.exit(1)

# program successful in creating the server socket using the input port number argument
print(f"PINGServer started with server IP: {server_ip}, port: {server_port}")

while True:
    data, addr = serverSock.recvfrom(1024)

     # extract header and payload
    recv_version, recv_client_id, recv_sequence_no, recv_timestamp, recv_size = struct.unpack('!B I I d I', data[:21])
    recv_payload = data[21:]
    
    # generate a random integer
    random_number = random.randint(1, 100)

    # server resumes normallly
    if random_number > args.packet_loss:
        print(f"IP:{addr[0]} :: Port:{addr[1]} :: ClientID:{recv_client_id} :: Seq#:{recv_sequence_no} :: RECEIVED")
        response_header = struct.pack('!B I I d I', recv_version, recv_client_id, recv_sequence_no, recv_timestamp, recv_size)
        response_packet = response_header + recv_payload
        serverSock.sendto(response_packet, addr)
    # ignore the packet and simulate a packet drop when random_number <= packet loss %
    else:
         print(f"IP:{addr[0]} :: Port:{addr[1]} :: ClientID:{recv_client_id} :: Seq#:{recv_sequence_no} :: DROPPED")

    print("----------Received Ping Request Packet Header----------")
    print(f"Version: {recv_version}")
    print(f"ClientID: {recv_client_id}")
    print(f"Sequence No.: {recv_sequence_no}")
    print(f"Time: {recv_timestamp:.3f}")
    print(f"Payload Size: {recv_size}")
    print("----------Received Ping Request Packet Payload----------")

    # decode the received payload from bytes to a UTF-8 string
    payload_info = recv_payload.decode('utf-8').split('::')
    print(f"Host: {payload_info[0]}")
    print(f"Class-name: {payload_info[1]}")
    print(f"User-name: {payload_info[2]}")
    print(f"Rest: {'::'.join(payload_info[3:])}")
    print("---------------------------------------")

    if random_number > args.packet_loss:
        print("----------- Ping Response Packet Header ----------")
        print(f"Version: {recv_version}")
        print(f"Client ID: {recv_client_id}")
        print(f"Sequence No.: {recv_sequence_no}")
        print(f"Time: {recv_timestamp:.3f}")
        print(f"Payload Size: {recv_size}")


    # Convert payload to uppercase
    response_payload = recv_payload.decode('utf-8').upper().encode('utf-8')

    print("---------- Ping Response Packet Payload -------------")
    response_payload_info = response_payload.decode('utf-8').split('::')
    print(f"Host: {response_payload_info[0]}")
    print(f"Class-name: {response_payload_info[1]}")
    print(f"User-name: {response_payload_info[2]}")
    print(f"Rest: {'::'.join(response_payload_info[3:])}")
    print("---------------------------------------")

    response_header = struct.pack('!B I I d I', recv_version, recv_client_id, recv_sequence_no, recv_timestamp, recv_size)
    response_packet = response_header + response_payload