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
    except:
        raise argparse.ArgumentTypeError(f"ERR - arg 1")

def packet_loss(value):
    try:
        ivalue = float(value)
        if fvalue < 0 or fvalue > 100:
            raise argparse.ArgumentTypeError(f"ERR = arg 2")
        return fvalue
    except ValueError:
        raise argparse.ArgumentTypeError(f"ERR - arg 2")

def positive_interger(value, arg_num):
    try: 
        ivalue = int(value)
        if ivalue < 1:
            raise argparse.ArgumentTypeError(f"ERR - arg {arg_num}")
        return ivalue
    except ValueError: 
        raise argparse.ArgumentTypeError(f"ERR - arg {arg_num}")

parser = argparse.ArgumentParser(description='UDP PINGServer')
parser.add_argument('server_port', type=port_number, help='Port that will listen on for incoming pings for clients')
parser.add_argument('packet_loss', type=loss_percentage, help='percentage of packet drop')
args = parser.parse_args()

server_ip = 'egr-v-cmsc440-1'
server_port = args.server_port

# if port number is already being taken by another active socket 
try:
    serverSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    serverSock.bind((server_ip, server_port))
except socket.error as e: 
    print("ERR - cannot create PINGServer socket using port number")
    sys.exit(1)

# program successful in creating the server socket using the input port number argument
print(f"PINGServer started with server IP: {server_ip}, port: {server_port}")

while True:
    data, addr = serverSock.recvfrom(1024)

    #simulate packet loss
    random_number = random.randint(1, 100)
    if random_number <= args.packet_loss:
        continue

    # extract header and payload

    # send the received packet back to the client
    serverSock.sendto(data, addr)