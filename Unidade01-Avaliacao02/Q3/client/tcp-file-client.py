import socket
import os
import time
import hashlib

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

    print(f"Conectado ao Servidor: {SERVER}:{PORT}\n")
    nomeArq = input("Digite o comando desejado: \n\n list: Lista os arquivos no servidor.\n sget <arquivo>: Faz o download de um único arquivo.\n mget <máscara>: Faz o download de múltiplos arquivos utilizando uma máscara.\n hash <arquivo>: Calcula o hash de um arquivo.\n 0: Encerra o programa.\n\nComando: ") # Input para receber o nome do arquivo.
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
                    dadosArq = dataTam.decode('utf-8') # Transforma o pacote contendo o tamanho em inteiro e printa o nome e tamanho.
                    print(dadosArq)
                    arquivo, tamArq = dadosArq.split(':')
                    tamArq = int(tamArq)
                    print(f"O arquivo '{arquivo}' possui o tamanho de {tamArq} Bytes.")
                    pedir_arquivo(arquivo, tamArq)
                    time.sleep(0.5)

    elif nomeArq== "hash":
        pedido = "4"
        print("Enviando pedido de Cálculo de Hash...\n")
        tcpSock.send(pedido.encode('utf-8'))

        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
        resposta = dataTam.decode('utf-8')

        arquivo = input(resposta)
        tcpSock.send(arquivo.encode('utf-8'))

        hashCalc = tcpSock.recv(2048).decode('utf-8')
        print(hashCalc)
        
        dataTam = tcpSock.recv(2048)
        resposta2 = dataTam.decode('utf-8')
        print(resposta2)
        break

    elif nomeArq== "eget":
        pedido = "5"
        print("Enviando pedido de continuar o download de um arquivo...\n")
        tcpSock.send(pedido.encode('utf-8'))

        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
        resposta = dataTam.decode('utf-8')

        arquivo = input(resposta)
        if not ":" in arquivo:
            tcpSock.send(arquivo.encode)
            dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
            resposta = dataTam.decode('utf-8')
            print(resposta)

        else:
            arquivo, hashPedido = arquivo.split(":")
            if hashPedido == "hash":
                print("Calculando hash do arquivo local...")
                path= os.path.join(DIRETORIO, arquivo)
                # Calculo do hash do arquivo na pasta files do CLIENTE
                if os.path.isfile(path):
                    with open (path, 'rb') as file:
                        leitura = file.read()
                        calc= hashlib.sha1(leitura).hexdigest()
                        client_hash= calc
                        tcpSock.send(f"{arquivo}:{client_hash}".encode())
                    dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
                    resposta = dataTam.decode('utf-8')

                    if resposta == "Os hashes do servidor e do cliente se distinguem um do outro\n":
                        print(resposta)
                        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
                        resposta = dataTam.decode('utf-8')
                        print(resposta)

                        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
                        resposta = dataTam.decode('utf-8')
                        print(resposta)

                        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
                        tamArq = int(dataTam.decode('utf-8')) # Transforma o pacote contendo o tamanho em inteiro e printa o nome e tamanho.
                        if tamArq > 0:  # Se o tamanho do arquivo for maior que 0, criaremos e salvaremos o arquivo
                            
                            with open(DIRETORIO + arquivo, "wb") as fd:
                                recebido = 0
                                while recebido < tamArq:
                                    data = tcpSock.recv(4096)  # Recebe dados em blocos
                                    fd.write(data)
                                    print("Lidos: ", len(data), "Bytes")  # Informa o número de bytes lidos
                                    recebido += len(data)
                                    print(f"O arquivo '{arquivo}' foi recebido com sucesso.")
                                    
                    else:
                        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.
                        resposta = dataTam.decode('utf-8')
                        print(resposta)
            
