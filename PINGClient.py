import socket
import time 
import argparse
import sys
import random
import string
import struct

# ensure port number is a positive integer less than 65536
def port_number(value):
    try:
        ivalue = int(value)
        if ivalue < 1 or ivalue > 65536:
            raise argparse.ArgumentTypeError(f"ERR - arg 2")
        return ivalue
    except ValueError:
        raise argparse.ArgumentTypeError(f"ERR - arg 2")

def positive_integer(value, arg_num):
    try: 
        ivalue = int(value)
        if ivalue < 1:
            raise argparse.ArgumentTypeError(f"ERR - arg {arg_num}")
        return ivalue
    except ValueError: 
        raise argparse.ArgumentTypeError(f"ERR - arg {arg_num}")

def valid_client_id(value):
    return positive_integer(value, 3)

def num_requests(value):
    return positive_integer(value, 4)

def wait_time(value):
    return positive_integer(value, 5)

# Argument parsing Ex: <hostname> or <ip> <port_number> <clientID> <number_of_ping_request> <wait_time>
parser = argparse.ArgumentParser(description='UDP PINGClient')
parser.add_argument('server_ip', type=str, help='Hostname or IP address of the ping server')
parser.add_argument('server_port', type=int, help='Port number the server is running on')
parser.add_argument('client_id', type=valid_client_id, help='ClientID')
parser.add_argument('num_requests', type=num_requests, help='Number of ping requests to send')
parser.add_argument('wait_time', type=wait_time, help='Number of wait seconds for each packet')
args = parser.parse_args()

try:
    host_ip = socket.gethostbyname(args.server_ip)
except socket.gaierror:
    print(f"ERR - Could not resolve the hostname: {args.server_ip}")
    sys.exit(1)

# create a UDP socket 
# domain which is the address family used when set up the socket: socket.AF_INET
# type of service: socket.SOCK_DGRAM 
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSock.settimeout(5)

print(f"PINGClient started with server IP: {args.server_ip}, port: {args.server_port}, client ID: {args.client_id}, packets: {args.num_requests}, wait: {args.wait_time}")

version = 1

received_packets = 0
min_rtt = float("inf")
max_rtt = float("-inf")
total_rtt = 0.0
total_payload_size = 0 

for sequence_no in range(1, args.num_requests + 1):
    host = args.server_ip
    class_name = "VCU-CMSC440-SPRING-2023"
    user_name = "Huyen, Huynh"
    max_rest_size = 300 - len(f"{host}::{class_name}::{user_name}::")
    rest = ''.join(random.choices(string.printable, k=random.randint(150, max_rest_size)))
    formatted_payload = f"{host}::{class_name}::{user_name}::{rest}"
    
    # custom header
    timestamp = time.time()
    payload_size = len(formatted_payload.encode())

    header = struct.pack('!B I I d I', version, args.client_id, sequence_no, timestamp, payload_size)

    packet = header + formatted_payload.encode()


    # send ping meassage to the server
    start_time = time.time()

    try:
        clientSock.sendto(packet, (host_ip, args.server_port))

        # if data is received back from server, print
        data, addr = clientSock.recvfrom(1024)
        end_time = time.time()

        # extract header and payload from the received packet
        recv_version, recv_client_id, recv_sequence_no, recv_timestamp, recv_size = struct.unpack('!B I I d I', data[:21])
        recv_payload = data[21:]

        # print request header fields
        print("-------- Ping Request Packet Header --------")
        print(f"Version: {recv_version}")
        print(f"ClientID: {recv_client_id}")
        print(f"Sequence No: {recv_sequence_no}")
        print(f"Time: {recv_timestamp:.3f}")
        print(f"Payload size: {recv_size}")

        # print request payload 
        username = "Huyen, Huynh"
        print("-------- Ping Request Packet Payload --------")
        print(f"Host: {args.server_ip}")
        print("Class-name: VCU-CMSC440-SPRING-2023")
        print("User-name: " + username)
        print(f"Rest: {rest}")
        print("---------------------------------------------")

        # print ping response if received 
        print(f"-------- Received Ping Response Packet Header --------")
        print(f"Version: {recv_version}")
        print(f"ClientID: {recv_client_id}")
        print(f"Sequence No.: {recv_sequence_no}")
        print(f"Time: {recv_timestamp:.3f}")
        print(f"Payload size: {recv_size}")

        # print ping response payload if received 
        print("-------- Received Ping Response Packet Payload --------")
        print(f"Host: {args.server_ip.upper()}")
        print("Class-name: VCU-CMSC440-SPRING-2023")
        print("User-name: " + username.upper())
        rest_data = recv_payload.decode().split('::', 3)[3]
        print(f"Rest: {rest_data.upper()}")


        # calculate RTT
        rtt = end_time - recv_timestamp
        min_rtt = min(min_rtt, rtt)
        max_rtt = max(max_rtt, rtt)
        total_rtt += rtt
        received_packets += 1
        print("RTT: {:.3f} seconds".format(rtt))

    except socket.error as e:
        print(f"ERR - Socket error: {e}")
        break

    except socket.timeout:
        print("----------- Ping Response Packet Timed-Out -----------")

    #update total payload size 
    total_payload_size += payload_size

    # time before sending the next ping
    time.sleep(args.wait_time)

# summary 
packet_loss_rate = ((args.num_requests - received_packets) / args.num_requests) 
avg_rtt = total_rtt / received_packets if received_packets > 0 else 0
avg_payload_size = total_payload_size / args.num_requests

print(f"Summary: {args.num_requests} :: {received_packets} :: {packet_loss_rate:.2f} :: {min_rtt:.6f} :: {max_rtt:.6f} :: {avg_rtt:.6f} :: {avg_payload_size:.2f}")