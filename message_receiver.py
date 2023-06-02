import socket
from time import sleep
import logging

class MessageReceiver:
    
    def __init__(self, tabela, vizinhos, semaforos) -> None:
        self.tabela_roteamento = tabela
        self.vizinhos = dict(zip(vizinhos, [0]*len(vizinhos)))
        self.semaforos = semaforos
    
    def run(self) -> None:
        server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        
        
        local = '10.32.160.172'
        ip_port = (local, 5000)
        buff_size = 1024
        
        server_socket.bind(ip_port)
        
        while(True):
            
            message, ip_address = server_socket.recvfrom(buff_size)
            ip_address = ip_address[0]
            message = message.decode('utf-8')
            
            print('[RECEIVER_RUN]: RECEIVED')
            
            if message == '!':
                self.vizinhos[ip_address] = 0
                tabela_str = f'*{ip_address};{1}*'
            else:
                tabela_str = message
            
            self.semaforos.semafTabela.acquire()
            atualizou = self.tabela_roteamento.update_tabela(tabela_str, ip_address, local)
            self.vizinhos[ip_address] = 0 # Zera timeout dos vizinhos
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
            for ip in self.vizinhos.keys():
                self.vizinhos[ip] += 1
                if self.vizinhos[ip] > 3:
                    self.tabela_roteamento.descarta_saida(ip)
                    print(f'[RECEIVER_TIMER]: NEGHBOR ROUTE DISCARDED {ip}')
                    print(self.tabela_roteamento)
                    
            print('[RECEIVER_TIMER]: TIMEOUT UPDATED')
            
            self.semaforos.semafTabela.release()

