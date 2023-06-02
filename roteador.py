
import sys
import threading
import logging
from pathlib import Path
from tabela_roteamento import TabelaRoteamento
from message_sender import MessageSender
from message_receiver import MessageReceiver

class Semaforos:
    def __init__(self) -> None:
        self.semafSender = threading.Condition()
        self.semafTabela = threading.Semaphore()

class Roteador:
    
    def __init__(self, vizinhos) -> None:
        self.vizinhos = vizinhos
        self.semaforos = Semaforos()
        self.tabela = TabelaRoteamento(self.vizinhos)
        print('\n'+' Tabela inicial '.center(38, '#'))
        print(self.tabela)
        print('\n')
    
    def main(self) -> None:
        
        sender = MessageSender(self.tabela, self.vizinhos, self.semaforos)
        receiver = MessageReceiver(self.tabela, self.vizinhos, self.semaforos)
        
        # return
        
        th_receiver = threading.Thread(target=receiver.run)
        th_receiver_timer = threading.Thread(target=receiver.timer)
        th_sender = threading.Thread(target=sender.run)
        th_sender_timer = threading.Thread(target=sender.timer)
        
        th_receiver.daemon = True
        th_receiver_timer.daemon = True
        th_sender.daemon = True
        th_sender_timer.daemon = True
        
        th_receiver.start()
        th_receiver_timer.start()
        th_sender.start()
        th_sender_timer.start()
        

class Aplicacao:
    def __init__(self) -> None:
        pass
    
    def ip_valido(self, ip) -> bool:
        return \
            ip.replace('.', '').isnumeric() and \
            sum([0 <= int(b) <= 255 for b in ip.split('.')]) == 4
    
    def menu(self) -> None:
        user_in = 1
        
        print('Informe um roteador vizinho\n > ', end='')
        vizinhos = []
        user_in = input().replace(' ', '')
        while not self.ip_valido(user_in):
            print('IP invalido. \n > ', end='')
            user_in = input().replace(' ', '')
        vizinhos.append(user_in)
        
        while True:
            print('Informe um roteador vizinho ou "1"\n > ', end='')
            user_in = input().replace(' ', '')
            if user_in == '1':
                break
            while not self.ip_valido(user_in):
                print('IP invalido. \n > ', end='')
                user_in = input().replace(' ', '')
            vizinhos.append(user_in)
        
        r = Roteador(vizinhos=vizinhos)
        r.main()
        
        quit_options = ('0', 'exit', 'quit', 'q')
        print(f'Inicializando')
        print(f'Para finalizar: {quit_options}')
        while True:
            q = input()
            if q in quit_options:
                break


def main():
    # n = (len(sys.argv) > 1) and sys.argv[1]

    # vizinhos = [
    #     '192.168.1.2',
    #     '192.168.1.4',
    # ]
    
    # r = Roteador(vizinhos)
    
    # print(r.tabela)
    # print(r.tabela.get_tabela_string())
    
    # r.main()
    
    app = Aplicacao()
    
    app.menu()

if __name__ == '__main__':
    main()
