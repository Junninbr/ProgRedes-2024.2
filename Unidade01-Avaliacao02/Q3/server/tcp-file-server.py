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

# Função de segurança para verificar se o arquivo está dentro do diretório 

def in_directory(base_directory, file_path):
    real_path = os.path.realpath(file_path) # Elimina qualquer arquivo com caminho contendo '..'
    if '..' in real_path.split(os.sep):
            client_socket(f"ERRO! O arquivo {file_path} contém '..', o que é proibido por questões de segurança.".encode('utf-8'))
            return False
    return real_path.startswith(os.path.realpath(base_directory)) # Verifica se o caminho real do arquivo está dentro do diretório base

# Função para cálcular o hash, apresentada nos comandos hash e eget
def calcular_hash(file_path, tamanho=None):
    with open(file_path, 'rb') as f:
        if tamanho:
            return hashlib.sha1(f.read(tamanho)).hexdigest()
        return hashlib.sha1(f.read()).hexdigest()


while True:

    try:
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
                arquivo = client_socket.recv(4096).decode()
    
                path = os.path.join(DIRETORIO, arquivo)
                if os.path.isfile(path):
                    tam = os.path.getsize(path)
                    print(f'Enviando o tamanho do arquivo {arquivo} ({tam} bytes) ao cliente {client_address}')
                    client_socket.sendall(str(tam).encode())
                    # Envia o arquivo em blocos de 2048 bytes
                    with open(path, 'rb') as file:
                        while chunk := file.read(4096):
                            client_socket.sendall(chunk)
                    print(f'Arquivo {arquivo} enviado com sucesso para {client_address}')
    
                elif '..' in filename: 
                    in_directory(DIRETORIO, file_path)
            # Caso o cliente solicite mais de um arquivo que contenham máscara (mget) - Comando 3
            elif filename == "3":
                print(f'Recebida a solicitação de arquivos com máscara do cliente {client_address}')
                client_socket.sendall(b"Envie a mascara de arquivos desejada (exemplo: *.jpg): ")
                mask = client_socket.recv(4096).decode()
                print(f"Recebida máscara de arquivos '{mask}' do cliente {client_address}")
                
                # Obtém a lista dos arquivos pertencentes a máscara 
                try:
                    files = glob.glob(os.path.join(DIRETORIO, mask))
                    qtd_files= len(files) # Quantidade de arquivos que atendem a máscara
                    client_socket.sendall(f'{qtd_files}'.encode())
                    if files:
                        client_socket.sendall(b'Arquivos encontrados. Iniciando envio...')
                        for file_path in files:
                            if in_directory(DIRETORIO, file_path):
                                filename = os.path.basename(file_path)
                                file_size = os.path.getsize(file_path)
                        print(f"Enviando arquivo '{filename}' ({file_size} bytes) ao cliente {client_address}")
                        client_socket.sendall(f"{filename}:{file_size}\n".encode()) # Enviando o nome e o tamanho do arquivo
            
                    # Enviar conteúdo do arquivo
                    with open(file_path, 'rb') as file:
                        while chunk := file.read(4096):
                            client_socket.sendall(chunk)
                    client_socket.sendall(b'FINAL\n') # Delimita o fim do arquivo
                    print(f'Arquivo {filename} enviado com sucesso ao cliente {client_address}')
                    time.sleep(0.5)
    
                # Avisa ao cliente que encerrou a transferencia dos arquivos
                    client_socket.sendall(b'Encerrado\n')
                    time.sleep(0.5)
                except FileNotFoundError:
                    print(f'A máscara digitada pelo cliente não está associada a nenhum dos arquivos do servidor! Portanto, não é possível enviar arquivos associados a mesma.')    
                    client_socket.sendall(b'0')
    
            # Caso o cliente solicite o hash SHA 1 de um arquivo (hash) - Comando 4
            elif filename == "4":
                    print (f'Recebida a solicitação do hash SHA 1 do cliente {client_address}')
                    client_socket.sendall(b'Envie o nome do arquivo e o posicionamento desejado (exemplo: barco.jpg:500): ')
                    hash= client_socket.recv(4096).decode()
                    name_arq, pos = hash.split(':') # Separação do nome do arquivo e da posição enviada pelo cliente
                    pos= int(pos)
                    if not ":" in hash:
                        erro = client_socket.sendall(f'ERRO! O formato de escrita para o hash {hash} está incorreto!'.encode())
                        print(erro) 
    
                    elif name_arq not in DIRETORIO:
                        erro = client_socket.sendall(f'ERRO! o arquivo {name_arq} não existe no diretório {DIRETORIO}'.encode())      
                        print(erro)    
    
                    elif ":" in hash:
                        path= os.path.join(DIRETORIO, name_arq)
                        if os.path.isfile(path):
                        # Cálculo do hash
                            with open (path, 'rb') as file:  # Lendo o arquivo em bytes até a posição solicitada pelo cliente
                                client_socket.sendall(f'Obtendo o hash SHA1 do arquivo {name_arq} até a posição {pos}').encode()
                                calc = calcular_hash(path)
                                client_socket.sendall(f'O hash SHA1 obtido do arquivo {name_arq} até a posição {pos} corresponde a : \n{calc} ').encode()
    
                        elif '..' in filename: 
                            in_directory(DIRETORIO, file_path)
    
            # Caso o cliente desejar continuar o download de um arquivo do servidor a partir de onde foi interrompido
            elif filename == "5":
                    print(f"Solicitação para continuar download do cliente {client_address}")
                    client_socket.sendall(b'Envie o nome do arquivo e o hash da parte baixada (exemplo: barco.jpg:hash): ')
                    novo_hash = client_socket.recv(4096).decode()
                    print(novo_hash)
                    name_arq, hash_cliente = novo_hash.split(':') # Separa nome e o hash para serem tratados separadamente
                    print(name_arq, hash_cliente)
                    path = os.path.join(DIRETORIO, name_arq)
    
                    if os.path.isfile(path):
                        hash_servidor = calcular_hash(path) 
                        print(hash_servidor)
    
                        if hash_cliente == hash_servidor:
                            client_socket.sendall(f'Os hashes dos arquivos são iguais, logo o arquivo na pasta files do cliente está completo'.encode('utf-8'))
                        else:
                            client_socket.sendall(f'Os hashes dos arquivos são diferentes, logo o arquivo na pasta files do cliente está incompleto'.encode('utf-8'))
                            tam_atual = int(client_socket.recv(4096).decode()) # Tamanho dos bytes do arquivo incompleto em files do cliente
                            print(tam_atual)
    
                            with open(path, 'rb') as file: # Seleciona o último byte onde o cliente interrompeu o download e armazena na variável resto
                                file.seek(tam_atual)  
                                resto = file.read() 
                                tam_arq= len(resto) # tam_arq armazena o tamanho dos bytes que faltam para completar o arquivo
                                client_socket.sendall(f'{int(tam_arq)}'.encode('utf-8')) # Envia o tamanho dos bytes que faltam para completar o arquivo
                                for i in range(0,tam_arq, 4096): # Completando os bytes do arquivo interrompido para formar o arquivo completo
                                    chunk = resto[i:i+4096]
                                    client_socket.sendall(chunk)
                                client_socket.sendall(f'Envio do restante do arquivo concluído.'.encode('utf-8'))
    
                    elif '..' in filename: 
                        in_directory(DIRETORIO, file_path)

                                
    except ConnectionResetError:
        print("Conexão perdida com o servidor, reinicie o programa para tentar uma nova conexão.")




    
    client_socket.close()