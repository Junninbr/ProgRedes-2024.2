import socket
import os
import glob
import hashlib
import time

# Configuração do servidor
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
ip = "127.0.0.1"
porta = 1234
server_address = (ip, porta)
DIRETORIO = 'files/'


# Vincula o servidor ao endereço e porta
server.bind(server_address)
server.listen(5)  # Configura o servidor para aceitar conexões

print(f'Servidor escutando em.... {ip}:{porta}')


while True:
    # Aguarda conexão de um cliente
    client_socket, client_address = server.accept()
    print(f'Cliente conectado: {client_address}')  

    while True:  # Mantém o loop ativo para múltiplas requisições do cliente
        filename= client_socket.recv(2048).decode()
        
        # Se o cliente desconectar, encerra o loop
        if not filename:
            print(f'Cliente {client_address} desconectado.')
            break
        elif filename == "0":
            print('Encerrando programa...')
        # Caso o cliente solicite a listagem de arquivos (list) - Comando 1
        if filename == "1":   
            print(f'Recebida solicitação de listagem de arquivos do cliente {client_address}')
            list_arq = os.listdir(DIRETORIO)
            listagem = []
            for file in list_arq:
                file_path = os.path.join(DIRETORIO, file)
                if os.path.isfile(file_path):
                    file_size = os.path.getsize(file_path)
                    listagem.append(f"{file} ({file_size} bytes)")
            if listagem:
                client_socket.sendall("\n".join(listagem).encode())
            else:
                client_socket.sendall(b'Nenhum arquivo encontrado no servidor.')
        
        # Caso o cliente solicite o envio de apenas um arquivo (sget) - Comando 2
        elif filename == "2":
            print(f'Recebida a solitação de apenas um arquivo do cliente {client_address}')
            client_socket.sendall(b'Envie o nome do arquivo desejado: ')
            arquivo = client_socket.recv(2048).decode()
            path = os.path.join(DIRETORIO, arquivo)
            if os.path.isfile(path):
                tam = os.path.getsize(path)
                print(f'Enviando o tamanho do arquivo {arquivo} ({tam} bytes) ao cliente {client_address}')
                client_socket.sendall(str(tam).encode())
                # Envia o arquivo em blocos de 2048 bytes
                with open(path, 'rb') as file:
                    while chunk := file.read(2048):
                        client_socket.sendall(chunk)
                print(f'Arquivo {arquivo} enviado com sucesso para {client_address}')

        # Caso o cliente solicite mais de um arquivo que contenham máscara (mget) - Comando 3
        elif filename == "3":
            print(f'Recebida a solicitação de arquivos com máscara do cliente {client_address}')
            client_socket.sendall(b"Envie a mascara de arquivos desejada (exemplo: *.jpg): ")
            mask = client_socket.recv(2048).decode()
            print(f"Recebida máscara de arquivos '{mask}' do cliente {client_address}")
            
            # Obtém a lista dos arquivos pertencentes a máscara 
            try:
                files = glob.glob(os.path.join(DIRETORIO, mask))
                if files:
                    client_socket.sendall(b'Arquivos encontrados. Iniciando envio...')
                    for file_path in files:
                        filename = os.path.basename(file_path) # Nome do arquivo 
                        file_size = os.path.getsize(file_path) # Tamanho do arquivo
                        print(f"Enviando arquivo '{filename}' ({file_size} bytes) ao cliente {client_address}")
                        client_socket.sendall(f"{filename}:{file_size}\0".encode()) 
                        # Envio do conteúdo do arquivo
                        with open (file_path, 'rb') as file: 
                            while chunk := file.read(2048):
                                client_socket.sendall(chunk)
                        print(f'Arquivo {filename} enviado com sucesso ao cliente {client_address} ')

                        time.sleep(0.5)
                    client_socket.sendall(b'Arquivos enviados com sucesso!')
            except FileNotFoundError:
                print(f'A máscara digitada pelo cliente não está associada a nenhum dos arquivos do servidor! Portanto, não é possível enviar arquivos associados a mesma.')    
                client_socket.sendall(b'0')

        # Caso o cliente solicite o hash SHA 1 de um arquivo (hash) - Comando 4
        elif filename == "4":
            try:
                print (f'Recebida a solicitação do hash SHA 1 do cliente {client_address}')
                client_socket.sendall(b'Envie o nome do arquivo e o posicionamento desejado (exemplo: barco.jpg:500): ')
                hash= client_socket.recv(2048).decode()
                if ":" in hash: # Separação do nome do arquivo e da posição enviada pelo cliente
                    name_arq, pos = hash.split(':')
                    pos= int(pos) # A posição será usada como limite para leitura do arquivo

                    path= os.path.join(DIRETORIO, name_arq)
                    if os.path.isfile(path):
                # Cálculo do hash
                        with open (path, 'rb') as file:  # Lendo o arquivo em bytes até a posição solicitada pelo cliente
                            limite = file.read(pos)
                            print(f'Obtendo o hash SHA1 do arquivo {name_arq} até a posição {pos}')   
                            calc= hashlib.sha1(limite).hexdigest() # Cálculo do hash SHA1
                            sha1 = (f'O hash SHA1 obtido do arquivo {name_arq} até a posição {pos} corresponde a : {calc}/n ')
                            client_socket.sendall(sha1.encode('utf-8'))
                            client_socket.sendall(b'Hash enviado com sucesso!')
            except Exception as e:
                if not ":" in hash: 
                    print(f'ERRO! O formato de escrita para o hash {hash} está incorreto!')
            
            except Exception as e:
                client_socket.sendall(f'ERRO! Falha no cálculo do hash: {str(e)}'.encode())
                   

        else: 
            print(f'O arquivo {arquivo} não foi encontrado no diretório {DIRETORIO}')
            client_socket.sendall(b'0')

    client_socket.close()