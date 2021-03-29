import os
import re
import time

import paramiko
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from klufe.constants import hostname, port


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
    client.connect(hostname, port=port, username=os.getenv('KLUFE_USERNAME'), password=os.getenv('KLUFE_PASSWORD'))
    conn = client.invoke_shell()
    conn.recv(10000)
    return client, conn


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voltage_on(request):
    client, conn = connect_ssh()
    conn.send('on\n')
    return receive_handler(client, conn)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def voltage_off(request):
    client, conn = connect_ssh()
    conn.send('off\n')
    return receive_handler(client, conn)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_DCVoltage(request):
    client, conn = connect_ssh()

    try:
        volts = request.data['volts']
    except KeyError:
        return Response(status=400, data={"detail": "Must include value for key 'volts' in request body"})

    conn.send(f'set dc {volts}\n')
    return receive_handler(client, conn)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def set_ACVoltage(request):
    client, conn = connect_ssh()

    try:
        volts = request.data['volts']
    except KeyError:
        return Response(status=400, data={"detail": "Must include value for key 'volts' in request body"})

    try:
        frequency = request.data['frequency']
    except KeyError:
        return Response(status=400, data={"detail": "Must include value for key 'frequency' in request body"})

    conn.send(f'set ac {volts} {frequency}\n')
    return receive_handler(client, conn)
