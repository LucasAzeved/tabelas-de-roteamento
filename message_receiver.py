import socket
from time import sleep
import logging

class MessageReceiver:
    
    def __init__(self, tabela, semaforos, ip_address) -> None:
        self.tabela_roteamento = tabela
        self.semaforos = semaforos
        self.server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        self.ip_address = ip_address
    
    def run(self) -> None:
        
        local = self.ip_address
        ip_port = (local, 5000)
        buff_size = 1024
        
        self.server_socket.bind(ip_port)
        
        while(True):
            
            message, ip_address = self.server_socket.recvfrom(buff_size)
            ip_address = ip_address[0]
            message = message.decode('utf-8')
            
            print('[RECEIVER_RUN]: RECEIVED')
            
            if message == '!':
                self.tabela_roteamento.vizinhos[ip_address] = 0
                tabela_str = f'*{ip_address};{1}'
            else:
                tabela_str = message
            
            self.semaforos.semafTabela.acquire()
            try:
                atualizou = self.tabela_roteamento.update_tabela(tabela_str, ip_address, local)
            except:
                print(tabela_str)
            self.tabela_roteamento.vizinhos[ip_address] = 0 # Zera timeout dos vizinhos
            self.semaforos.semafTabela.release()
            
            print('[RECEIVER_RUN]: TABLE UPDATED') 
            
            if atualizou:
                print(self.tabela_roteamento)
                self.semaforos.semafSender.acquire()
                self.semaforos.semafSender.notify()
                self.semaforos.semafSender.release()
    
    def timer(self) -> None:
        
        while(True):

            sleep(10)
            
            self.semaforos.semafTabela.acquire()
            for ip in self.tabela_roteamento.vizinhos.keys():
                self.tabela_roteamento.vizinhos[ip] += 1
                if self.tabela_roteamento.vizinhos[ip] > 3:
                    self.tabela_roteamento.descarta_saida(ip)
                    print(f'[RECEIVER_TIMER]: NEGHBOR ROUTE DISCARDED {ip}')
                    print(self.tabela_roteamento)
                    
            print('[RECEIVER_TIMER]: TIMEOUT UPDATED')
            
            self.semaforos.semafTabela.release()


if __name__ == '__main__':
    
    import threading
    
    class Semaforos:
        def __init__(self) -> None:
            self.semafSender = threading.Condition()
            self.semafTabela = threading.Semaphore()
    
    from tabela_roteamento import TabelaRoteamento
    
    vizinhos = [
        '10.32.162.190'
        # '10.32.163.25'
    ]
    
    sf = Semaforos()
    tb = TabelaRoteamento(vizinhos)
    
    receiver = MessageReceiver(tb, sf)
    
    print(receiver.get_ip())
