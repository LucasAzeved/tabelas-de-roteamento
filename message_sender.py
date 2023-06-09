
import socket
from time import sleep

class MessageSender:
    def __init__(self, tabela, semaforos) -> None:
        self.tabela_roteamento = tabela
        self.semaforos = semaforos
    
    def send(self, send_data, clientSocket: socket.socket) -> None:
        for ip in self.tabela_roteamento.vizinhos.keys():
            try:
                clientSocket.sendto(send_data, (ip, 5000)) # (IP, Porta)
            except:
                print('Erro no send.')

    
    def run(self) -> None:
        
        clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.send(r'!'.encode(), clientSocket)
        
        while True:
            self.semaforos.semafSender.acquire()
            self.semaforos.semafSender.wait()
            
            tabela_str = self.tabela_roteamento.get_tabela_string()
            send_data = tabela_str.encode()
            self.send(send_data, clientSocket)
            
            print('[SENDER_RUN]: SENT')
            
            self.semaforos.semafSender.release()
    
    def timer(self) -> None:
        
        sleep(2)
        
        while(True):
            
            self.semaforos.semafSender.acquire()
            self.semaforos.semafSender.notify()
            self.semaforos.semafSender.release()
            
            print('[SENDER_TIMER]: NOTIFIED')
            
            sleep(10)

if __name__ == '__main__':

    import threading

    class Semaforos:
        def __init__(self) -> None:
            self.semafSender = threading.Condition()
            self.semafTabela = threading.Semaphore()

    from tabela_roteamento import TabelaRoteamento

    clientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

    vizinhos = [
        '10.32.162.190'
        # '10.32.163.25'
    ]

    sf = Semaforos()
    tb = TabelaRoteamento(vizinhos)

    sender = MessageSender(tb, sf)

    send_data = '*192.168.1.2;2*192.168.1.4;2'.encode()

    sender.send(send_data, clientSocket)