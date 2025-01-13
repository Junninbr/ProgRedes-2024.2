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
    if os.path.exists(DIRETORIO + arquivo):
        resp = input(f"O arquivo '{arquivo}' já existe, deseja sobrescrever? S ou N: ")
        if resp != "s" and resp != "S":
            print("Operação cancelada.")
            return
        else:
            print(f"Substituindo o arquivo '{arquivo}'...")
            
    
    if tamArq > 0:
        print(f"Salvando o arquivo '{arquivo}' localmente...")
        with open(DIRETORIO + arquivo, "wb") as fd:
            recebido = 0
            while recebido < tamArq:
                data = tcpSock.recv(4096)
                fd.write(data)
                print("Lidos:", recebido, "bytes")
                recebido += len(data)
            print(f"O arquivo '{arquivo}' foi recebido com sucesso.\n")
            time.sleep(2)
            print("Voltando ao menu principal...\n")
            
    else:
        print("Erro: Arquivo não encontrado.")

print(f"Conectado ao Servidor: {SERVER}:{PORT}\n")

while True:
        try:
            nomeArq = input("Digite o comando desejado: \n\n list: Lista os arquivos no servidor.\n sget -> <arquivo>: Faz o download de um único arquivo.\n mget -> <máscara>: Faz o download de múltiplos arquivos utilizando uma máscara.\n cget -> <arquivo>: Continua o download de onde parou em caso de desconexão.\n hash -> <arquivo>: Calcula o hash de um arquivo.\n 0: Encerra o programa.\n\nComando: ") # Input para receber o nome do arquivo.
            if nomeArq == "0":
                print("Encerrando programa...")
                tcpSock.close()
                break
            
            elif nomeArq == "list":
                pedido = "1"
                print("Enviando pedido de listagem dos arquivos.\n")
                tcpSock.send(pedido.encode('utf-8'))
                dataTam = tcpSock.recv(2048)
                resposta = str(dataTam.decode('utf-8'))
                print(f"{resposta}\n")
                time.sleep(5)
                print("Voltando ao menu principal...\n")
                time.sleep(2)

            elif nomeArq == "sget":
                pedido = "2"
                print("Enviando pedido de download de um único arquivo ao servidor...\n")
                tcpSock.send(pedido.encode('utf-8'))
                
                dataTam = tcpSock.recv(2048)
                resposta = (dataTam.decode('utf-8'))
                arquivo = input(resposta)

                laco = True
                while laco:
                    if arquivo[0:2] == "..": 
                        print ("Enviando pedido a", (SERVER, PORT), "para", arquivo)
                        tcpSock.send(arquivo.encode('utf-8'))
                        dataTam = tcpSock.recv(2048)
                        resposta = (dataTam.decode('utf-8'))
                        print(resposta)

                    else:
                        print ("Enviando pedido a", (SERVER, PORT), "para", arquivo)
                        tcpSock.send(arquivo.encode('utf-8'))

                        dataTam = tcpSock.recv(2048)

                        try:
                            tamArq = int(dataTam.decode('utf-8'))
                            print(f"O arquivo '{arquivo}' possui o tamanho de {tamArq} Bytes.")
                        except ValueError:
                            continue

                        pedir_arquivo(arquivo, tamArq)
                        laco = False

            elif nomeArq == "mget":
                pedido = "3"
                print("Enviando pedido de download de múltiplos arquivos por máscara ao servidor...\n")
                tcpSock.send(pedido.encode('utf-8'))
                resposta = tcpSock.recv(4096).decode('utf-8')
    
                print(resposta)
                arquivo_mask = input("Digite a máscara de arquivos desejada (ex.: *.jpg): ")
                tcpSock.send(arquivo_mask.encode('utf-8'))
    
                qtd_arquivos = int(tcpSock.recv(4096).decode('utf-8'))
                if qtd_arquivos == 0:
                    print("Nenhum arquivo encontrado com a máscara fornecida.")
                   
    
                print(f"{qtd_arquivos} arquivos encontrados. Recebendo...")
                # Verifique se o formato dos metadados é válido
                while True:
                    # Receber metadados do arquivo
                    metadados = tcpSock.recv(4096).decode('utf-8').strip()
                    
                    if metadados == 'Encerrado':
                            print("Todos os arquivos foram recebidos com sucesso!")
                            break
        
                    elif ':' not in metadados:
                        print(f"Erro nos metadados recebidos: {metadados}")
                        continue  

                     
                    nome_arquivo, tamanho_arquivo = metadados.split(':')
                    tamanho_arquivo = int(tamanho_arquivo)
                    print(f"Recebendo arquivo '{nome_arquivo}' ({tamanho_arquivo} bytes)")
                    caminho_arquivo = os.path.join( DIRETORIO, nome_arquivo)

                    if os.path.exists(caminho_arquivo):
                        resposta = input(f"O arquivo '{nome_arquivo}' já existe. Deseja sobrescrevê-lo? (s/n): ").strip().lower()
                        if resposta != 's':
                            print(f"Arquivo '{nome_arquivo}' não será sobrescrito. Pulando...")
                            continue  # Não sobrescreve o arquivo e passa para o próximo
        
                # Receber conteúdo do arquivo
                    with open(nome_arquivo, 'wb') as f:
                        recebido = 0
                        while recebido < tamanho_arquivo:
                            dados = tcpSock.recv(min(4096, tamanho_arquivo - recebido))
                            if not dados:
                                break
                            f.write(dados)
                            recebido += len(dados)
        
                    print(f"Arquivo '{nome_arquivo}' recebido com sucesso.")


            elif nomeArq== "hash":
                pedido = "4"
                print("Enviando pedido de Cálculo de Hash...\n")
                tcpSock.send(pedido.encode('utf-8'))

                dataTam = tcpSock.recv(2048)
                resposta = dataTam.decode('utf-8')

                arquivo = input(resposta)
                laco = True
                while laco:
                    if arquivo[0:2] == "..":
                        tcpSock.send(arquivo.encode('utf-8'))
                        dataTam = tcpSock.recv(2048)
                        resposta = (dataTam.decode('utf-8'))
                        print(resposta)
                        laco = False

                    else:
                        hashCalc = tcpSock.recv(2048).decode('utf-8')
                        print(hashCalc)
                        
                        dataTam = tcpSock.recv(2048)
                        resposta2 = dataTam.decode('utf-8')
                        print(resposta2)
                        laco = False

            elif nomeArq== "cget":
                pedido = "5"
                print("Enviando pedido de continuar o download de um arquivo...\n")
                tcpSock.send(pedido.encode('utf-8'))

                dataTam = tcpSock.recv(2048)
                resposta = dataTam.decode('utf-8')

                arquivo = input(resposta)
                laco = True
                while laco:
                    if arquivo[0:2] == "..":
                        tcpSock.send(arquivo.encode('utf-8'))
                        dataTam = tcpSock.recv(2048)
                        resposta = (dataTam.decode('utf-8'))
                        print(resposta)
                        laco = False

                    elif not ":" in arquivo:
                        tcpSock.send(arquivo.encode)
                        dataTam = tcpSock.recv(2048)
                        resposta = dataTam.decode('utf-8')
                        print(resposta)
                        laco = False

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
                                    print(client_hash)
                                    tcpSock.send(f"{arquivo}:{client_hash}".encode())
                                    
                                dataTam = tcpSock.recv(2048)
                                resposta = dataTam.decode('utf-8')
                                print(resposta)

                                if resposta == "Os hashes dos arquivos são diferentes, logo o arquivo na pasta files do cliente está incompleto":
                                    print(resposta)
                        
                                    with open (path, 'rb') as file:
                                        leitura = file.read()
                                        arqLocal = len(leitura)
                                        tcpSock.send(f"{int(arqLocal)}".encode())

                                    dataTam = tcpSock.recv(2048)
                                    tamArq = int(dataTam.decode('utf-8'))
                                    print(f"O restante do arquivo '{arquivo}' possui {tamArq} bytes.\n")
                                    print("Baixando o restante do arquivo, aguarde...\n")
                                    time.sleep(3)

                                    if tamArq > 0:
                                        
                                        with open(DIRETORIO + arquivo, "ab") as fd:
                                            recebido = 0
                                            while recebido < tamArq:
                                                data = tcpSock.recv(4096)
                                                fd.write(data)
                                                print("Lidos: ", recebido, "Bytes")  
                                                recebido += len(data)
                                        dataTam = tcpSock.recv(2048) 
                                        resposta = dataTam.decode('utf-8')
                                        print(resposta)

                                else:
                                    dataTam = tcpSock.recv(2048) 
                                    resposta = dataTam.decode('utf-8')
                                    print(resposta)
                        laco = False

            else:
                print("Comando inválido, digite um comando corretamente.\n")
        except ConnectionResetError:
                print("Conexão perdida com o servidor, reinicie o programa para tentar uma nova conexão.")
                break