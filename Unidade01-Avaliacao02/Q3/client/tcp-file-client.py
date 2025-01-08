import socket
import os
import time

SERVER = '127.0.0.1' 
PORT = 1234 
DIRETORIO = "files/"

tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSock.connect((SERVER, PORT))

def pedir_arquivo(arquivo, tamArq):
    if os.path.exists(DIRETORIO + arquivo):  # Verifica se o arquivo já existe
        resp = input(f"O arquivo '{arquivo}' já existe, deseja sobrescrever? S ou N: ")
        if resp != "S":
            print("Operação cancelada.")
            return
        else:
            print(f"Substituindo o arquivo '{arquivo}'...")
            
    
    if tamArq > 0:  # Se o tamanho do arquivo for maior que 0, criaremos e salvaremos o arquivo
        print(f"Salvando o arquivo '{arquivo}' localmente...")
        with open(DIRETORIO + arquivo, "wb") as fd:
            recebido = 0
            while recebido < tamArq:
                data = tcpSock.recv(4096)  # Recebe dados em blocos
                fd.write(data)
                print("Lidos: ", len(data), "Bytes")  # Informa o número de bytes lidos
                recebido += len(data)
            print(f"O arquivo '{arquivo}' foi recebido com sucesso.")
            
    else:
        print("Erro: Arquivo não encontrado.")

# Loop para iterar o pedido do arquivo. 
while True:
    nomeArq = input("Digite o comando desejado ou digite 0 para sair: ") # Input para receber o nome do arquivo.
    if nomeArq == "0": # Caso seja digitado 0, a conexão com o servidor é fechado e o loop é encerrado.
        tcpSock.close()
        print("Encerrando programa...")
        tcpSock.close()
        break
    
    elif nomeArq == "list":
        pedido = "1"
        print("Enviando pedido de listagem dos arquivos.\n")
        tcpSock.send(pedido.encode('utf-8')) # Enviará o pedido codificado em UTF-8.
        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
        resposta = str(dataTam.decode('utf-8'))
        print(resposta)
        break


    elif nomeArq == "sget":
        pedido = "2"
        print("Enviando pedido de download de um único arquivo ao servidor...\n")
        tcpSock.send(pedido.encode('utf-8'))
        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
        resposta = str(dataTam.decode('utf-8'))
        
        
        arquivo = input(resposta)
        print ("Enviando pedido a", (SERVER, PORT), "para", arquivo) # Caso seja pedido um arquivo, será printado o nome em si ao servidor conectado.
        tcpSock.send(arquivo.encode('utf-8')) # Enviará o pedido codificado em UTF-8.

        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.

        try:
            tamArq = int(dataTam.decode('utf-8')) # Transforma o pacote contendo o tamanho em inteiro e printa o nome e tamanho.
            print(f"O arquivo '{arquivo}' possui o tamanho de {tamArq} Bytes.")
        except ValueError: # Caso o valor recebido seja 0, dará essa exceção.
            continue

        pedir_arquivo(arquivo, tamArq)

    elif nomeArq == "mget":
        pedido = "3"
        print("Enviando pedido de download de múltiplos arquivos por máscara ao servidor...\n")
        tcpSock.send(pedido.encode('utf-8'))
        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
        resposta = str(dataTam.decode('utf-8'))
        
        
        arquivo = input(resposta)

        if arquivo[0:2] != "*.":
            print("Erro de sintaxe, digite um nome válido. Ex.: *.jpg, *.xml.")
        else:
            print("Enviando pedido a", (SERVER, PORT), "para todos os arquivos contendo", arquivo) # Caso seja pedido um arquivo, será printado o nome em si ao servidor conectado.
            tcpSock.send(arquivo.encode('utf-8')) # Enviará o pedido codificado em UTF-8.

            dataTam = tcpSock.recv(2048)
            resposta = str(dataTam.decode('utf-8'))


            while True:   
                 
                dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
                print('teste: ', dataTam)
            
                if dataTam == b'Encerrado':
                    print(f'Todos os arquivos foram recebidos com sucesso!')
                    break
                else:
                    dadosArq = str(dataTam.decode('utf-8')) # Transforma o pacote contendo o tamanho em inteiro e printa o nome e tamanho.
                    print(dadosArq)
                    arquivo, tamArq = dadosArq.split(':')
                    tamArq = int(tamArq)
                    print(f"O arquivo '{arquivo}' possui o tamanho de {tamArq} Bytes.")
                    pedir_arquivo(arquivo, tamArq)
                    time.sleep(0.5)
