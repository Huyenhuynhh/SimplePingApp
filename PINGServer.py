import socket
import argparse

parser = argparse.ArgumentParser(description='UDP PINGServer')
parser.add_argument('port', help='Port that will listen on for incoming pings for clients')
parser.add_argument('loss', help='percentage of packet drop')

