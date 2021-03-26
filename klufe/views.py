import paramiko
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import re
import time


@api_view(['POST'])
@permission_classes([AllowAny])
def setDC(request):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    client.connect('hpt-k5700.colab.duke.edu', port=2222, username='admin6', password='foxY458')
    conn = client.invoke_shell()

    conn.recv(10000)
    conn.send('on\n')

    n = 0
    while n < 3:
        time.sleep(0.5)
        if conn.recv_ready():
            break

    prompt = conn.recv(10000).decode('ascii')

    client.close()
    return Response({re.split(r'\x1B[\[0-9;]*m', prompt)[2]})
