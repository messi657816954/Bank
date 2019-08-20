import json
import socket


#HOST = "localhost"
#PORT = 15555
#NOM = 'SOCKET_ECOUTE'
import time

HOST = "192.168.10.219"
PORT = 5010
# NOM = 'SOCKET_ECOUTE'

class SocketHandler:

  def __init__(self, sock=None):
    if sock is None:
      self.sock = socket.socket(
      socket.AF_INET, socket.SOCK_STREAM)
    else:
      self.sock = sock
    self.connect(HOST, PORT)


  def connect(self, host, port):
    self.sock.connect((host, port))


  def send(self, msg):
    totalsent = 0
    MSGLEN = len(msg)
    while totalsent < MSGLEN:
      sent = self.sock.send(msg[totalsent:])
      if sent == 0:
        raise RuntimeError("socket connection broken")

      totalsent = totalsent + sent

  # def receive(self, EOFChar=b'\x036'):
  def receive(self, EOFChar=b'\x036'):
    # msg = b''
    msg = b''
    MSGLEN = 256
    while len(msg) < MSGLEN:
      chunk = self.sock.recv(MSGLEN-len(msg))
      if chunk.find(EOFChar)!= -1:
        msg = msg + chunk
        return msg

      msg = msg + chunk
      return msg

  def get_response(self,MSG_CODE,data):
    s = "[{'msg_code': %s, 'params': %s}]" % (MSG_CODE,data)
    print('sendsendsendsend', bytes(s, encoding='utf8'))
    self.send(bytes(s, encoding='utf8'))
    #  transfert la reponse
    #self.sock.settimeout(15.0)
    recep = self.receive()
    print('receprecepreceprecep', recep)

    ''' formatage de la reponse en json '''
    rep_json = recep.decode('utf-8')#.replace("'", '"')
    print('rep_jsonrep_jsonrep_jsonrep_json',rep_json)
    ''' formatage json enliste '''
    data_list = json.loads(str(rep_json))
    #data_list = json.dumps(rep_json)
    print("data_listdata_listdata_list",data_list)

    return data_list




































