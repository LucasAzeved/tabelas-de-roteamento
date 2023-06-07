
import socket
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
    
    def __init__(self, vizinhos, ip_address) -> None:
        self.vizinhos = vizinhos
        self.ip_address = ip_address
        self.semaforos = Semaforos()
        self.tabela = TabelaRoteamento(self.vizinhos)
        print('\n'+' Tabela inicial '.center(38, '#'))
        print(self.tabela)
        print('\n')
    
    def main(self) -> None:
        
        sender = MessageSender(self.tabela, self.semaforos)
        receiver = MessageReceiver(self.tabela, self.semaforos, self.ip_address)
        
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
    
    def get_ip(self):
        server_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
        server_socket.settimeout(0)
        try:
            # doesn't even have to be reachable
            server_socket.connect(('10.254.254.254', 1))
            IP = server_socket.getsockname()[0]
        except Exception:
            IP = '127.0.0.1'
        finally:
            server_socket.close()
        return IP
    
    def ip_valido(self, ip) -> bool:
        return \
            ip.replace('.', '').isnumeric() and \
            sum([0 <= int(b) <= 255 for b in ip.split('.')]) == 4
    
    def vizinhos_pelo_console(self) -> list:
        
        vizinhos = []
        print('Informe um roteador vizinho\n > ', end='')
        user_in = input().replace(' ', '')
        if self.ip_valido(user_in):
            vizinhos.append(user_in)
        else:
            print('IP invalido.')
        
        while True:
            print('Informe um roteador vizinho ou "1"\n > ', end='')
            user_in = input().replace(' ', '')
            if user_in == '1':
                break
            if self.ip_valido(user_in):
                vizinhos.append(user_in)
            else:
                print('IP invalido.')
        
        return vizinhos
    
    def vizinhos_pelo_arquivo(self, local_ip) -> list:
        
        print('Informe o nome do arquivo txt:\n > ', end='')
        file = input().replace('.txt', '') + '.txt'
        
        file = Path(__file__).parent.resolve() / file
        
        with open(file, 'r') as f:
            content = [l.split(';') for l in f.read().split('\n')]
        
        vizinhos = dict(zip([ip for ip, _ in content], [[] for _ in content]))
        
        for k, v in content:
            vizinhos[k].append(v)
            
        return vizinhos[local_ip]
    
    def menu(self) -> None:
        
        user_in = ''
        vizinhos = ''
        local_ip = self.get_ip()
        
        while user_in not in ('1', '2'):
            print(
                'Informar vizinhos:\n'+
                '  1 - Pelo terminal\n'+
                '  2 - Por arquivo\n' + 
                ' > ', end=''
                )
            user_in = input()
            if user_in == '1':
                vizinhos = self.vizinhos_pelo_console()
                break
            elif user_in == '2':
                vizinhos = self.vizinhos_pelo_arquivo(local_ip)
                break
            else:
                pass

        r = Roteador(vizinhos=vizinhos, ip_address=local_ip)
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

