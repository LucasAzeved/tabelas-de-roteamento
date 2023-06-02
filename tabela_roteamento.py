
from tabulate import tabulate
from dataclasses import dataclass, field

@dataclass
class TabelaRoteamento:
    vizinhos: list[str]
    tabela: dict[str, list[int, str]] = field(init=False) # formato: {'ip_destino': ['métrica', 'ip_saída']}
    
    def __post_init__(self):
        self.vizinhos = dict(zip(self.vizinhos, [0]*len(self.vizinhos)))
        self.tabela = {ip: [1, ip] for ip in self.vizinhos.keys()}
        
    
    def update_tabela(self, tabela_str: str, ip_address: str, local: str) -> bool:
        """
        Atualize a tabela de roteamento a partir da string recebida.
        """
        recebida = [[l.split(';')[0], int(l.split(';')[-1])] 
                        for l in tabela_str[1:-1].split('*')]
        
        atualizou = False
        
        for destino, metrica in recebida:
            if destino == local:
                continue
            if destino not in self.tabela.keys():
                if destino in self.vizinhos.keys():
                    self.tabela[destino] = [1, ip_address]
                else:
                    self.tabela[destino] = [metrica+1, ip_address]
                atualizou = True
            elif (metrica+1) < self.tabela[destino][0]:
                self.tabela[destino] = [metrica+1 , ip_address]
                atualizou = True
        
        return atualizou
    
    def descarta_saida(self, ip_address: str) -> None:
        for destino, ( _ , saida) in list(self.tabela.items()):
            if saida == ip_address:
                self.tabela.pop(destino)
    
    def get_tabela_string(self) -> str:
        """
        Converte a tabela de roteamento para string.
        *IP_Destino;Métrica*IP_Destino;Métrica*...*
        """
        tabela_str = '*' + '*'.join([destino+';'+str(metrica) for destino, (metrica, _ ) in self.tabela.items()]) + '*'
        
        return tabela_str
    
    def __repr__(self) -> str:
        t = [[destino, metrica, saida] for destino, (metrica, saida) in self.tabela.items()]
        return tabulate(t, headers=['Destino', 'Métrica', 'Saída'], tablefmt='pretty', stralign='center')


if __name__ == '__main__':
    
    vizinhos = [
        '192.168.1.2',
        '192.168.1.4',
    ]
    
    t = TabelaRoteamento(vizinhos)
    
    print(t)
    print(t.vizinhos)
    # print(t.get_tabela_string())
    
    # tab_up = '*192.168.1.2;2*192.168.1.4;2*'
    # tab_up = '*192.168.1.2;2*192.168.1.4;2*'
    
    # t.update_tabela(tab_up, 'NOVA ROTA')
    
    # print(t)
    # print(t.get_tabela_string())