import paramiko
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import re
import time


def receive_handler(client, conn):
    n = 0
    while n < 3:
        time.sleep(0.5)
        if conn.recv_ready():
            break
    prompt = conn.recv(10000).decode('ascii')
    client.close()
    return Response({re.split(r'\x1B[\[0-9;]*m', prompt)[2]})

def connect_ssh():
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect('hpt-k5700.colab.duke.edu', port=2222, username='admin6', password='foxY458')
    conn = client.invoke_shell()
    conn.recv(10000)
    return client, conn


@api_view(['POST'])
@permission_classes([AllowAny])
def voltage_on(request):
    client, conn = connect_ssh()
    conn.send('on\n')

    return receive_handler(client, conn)


@api_view(['POST'])
@permission_classes([AllowAny])
def voltage_off(request):
    client, conn = connect_ssh()

    conn.recv(10000)
    conn.send('off\n')

    return receive_handler(client, conn)


@api_view(['POST'])
@permission_classes([AllowAny])
def set_DCVoltage(request, volts=0):
    client, conn = connect_ssh()

    # TODO: Where get volts
    conn.recv(10000)
    conn.send('set dc ' + volts + '\n')

    return receive_handler(client, conn)


@api_view(['POST'])
@permission_classes([AllowAny])
def set_ACVoltage(request, volts=0, freq=0):
    client, conn = connect_ssh()

    # TODO: Where get volts and frequency
    conn.recv(10000)
    conn.send('set ac ' + volts + ' ' + freq + '\n')

    return receive_handler(client, conn)
