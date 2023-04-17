import socket
import time 
import argparse
import sys
import random
import string
import struct

def port_number(value):
    try:
        ivalue = int(value)
        if ivalue < 1 or ivalue > 65535:
            raise argparse.ArgumentTypeError(f"ERR - arg 2")
        return ivalue
    except:
        raise argparse.ArgumentTypeError(f"ERR - arg 2")

def positive_integer(value, arg_num):
    try: 
        ivalue = int(value)
        if ivalue < 1:
            raise argparse.ArgumentTypeError(f"ERR - arg {arg_num}")
        return ivalue
    except ValueError: 
        raise argparse.ArgumentTypeError(f"ERR - arg {arg_num}")

def num_requests(value):
    return positive_integer(value, 4)

def wait_time(value):
    return positive_integer(value, 5)

class CustomArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        arg_mapping = {
            "server": 1,
            "server_port": 2,
            "client_id": 3,
            "num_requests": 4,
            "wait_time": 5
        }
        
        for arg_name, arg_number in arg_mapping.items():
            if arg_name in message:
                sys.stderr.write(f'ERR - {}')

# Argument parsing Ex: <hostname> or <ip> <port_number> <clientID> <number_of_ping_request> <wait_time>
parser = argparse.ArgumentParser(description='UDP PINGClient')
parser.add_argument('server', help='Hostname or IP addess of the ping server')
parser.add_argument('server_port', type=int, help='Port number the server is running on')
parser.add_argument('client_id', type=int, help='ClientID')
parser.add_argument('num_requests', type=int, help='Number of ping requests to send')
parser.add_argument('wait_time', type=int, help='Number of wait seconds for each packet')
args = parser.parse_args()

client_ip = '127.0.0.1'
client_port = 11000

# create a UDP socket 
# domain which is the address family used when set up the socket: socket.AF_INET
# type of service: socket.SOCK_DGRAM 
clientSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
clientSock.settimeout(args.wait_time)

# bind the socket to the clients IP address and port 
clientSock.bind((client_ip, client_port))

print(f"PINGClient started with server IP: {args.server}, port: {args.server_port}, client ID: {args.client_id}, packets: {args.num_requests}, wait: {args.wait_time}")

# handle excetion
try:
    # hostname or ip of the ping server
    server_ip = socket.gethostbyname(args.server)
except socket.gaierror:
    print("ERR - Unable to resolve hostname")
    sys.exit(1)

version = 1

received_packets = 0
min_rtt = float("inf")
max_rtt = float("-inf")
total_rtt = 0.0
total_payload_size = 0 

for sequence_no in range(1, args.num_requests + 1):
    random_data_size = random.randint(150, 300)
    random_data = ''.join(random.choices(string.printable, k=random_data_size))

    # custom header
    timestamp = time.time()
    header = struct.pack('!B I I d I', version, args.client_id, sequence_no, timestamp, random_data_size)


    message = f"Ping! from ClientID: {args.client_id}{random_data}"
    packet = header + message.encode()

    # send ping meassage to the server
    start_time = time.time()

    try:
        clientSock.sendto(message.encode(), (server_ip, args.server_port))

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
        print(f"Time: {recv_timestamp}")
        print(f"Payload size: {recv_size}")

        # print request payload 
        username = "Huyen, Huynh"
        print("-------- Ping Request Packet Payload --------")
        print(f"Host: {args.server}")
        print("Class-name: VCU-CMSC440-SPRING-2023")
        print("User-name: " + username)
        print(f"Rest: {random_data}")
        print("---------------------------------------------")

        # print ping response if received 
        print(f"-------- Received Ping Response Packet Header --------")
        print(f"Version: {recv_version}")
        print(f"ClientID: {recv_client_id}")
        print(f"Sequence No: {recv_sequence_no}")
        print(f"Time: {recv_timestamp}")
        print(f"Payload size: {recv_size}")

        # print ping response payload if received 
        print("-------- Received Ping Response Packet Payload --------")
        print(f"Host: {args.server.upper()}")
        print("Class-name: VCU-CMSC440-SPRING-2023")
        print("User-name: " + username.upper())
        print(f"Rest: {recv_payload.decode().upper()}") 

        # calculate RTT
        rtt = end_time - recv_timestamp
        min_rtt = min(min_rtt, rtt)
        max_rtt = max(max_rtt, rtt)
        total_rtt += rtt
        received_packets += 1
        print("RTT: {:.6f} seconds".format(rtt))

    except socket.error as e:
        print(f"ERR - Socket error: {e}")
        break

    except socket.timeout:
        print("----------- Ping Response Packet Timed-Out -----------")

    # time before sending the next ping
    time.sleep(1)

# summary 
packet_loss_rate = ((args.num_requests - received_packets) / args.num_requests) * 100
avg_rtt = total_rtt / received_packets if received_packets > 0 else 0
avg_payload_size = total_payload_size / args.num_requests

print(f"Summary: {args.num_requests} :: {received_packets} :: {packet_loss_rate:.2f}% :: {min_rtt:.6f} :: {max_rtt:.6f} :: {avg_rtt:.6f} :: {avg_payload_size:.2f}")