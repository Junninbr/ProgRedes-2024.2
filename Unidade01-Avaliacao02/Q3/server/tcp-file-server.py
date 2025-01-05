import socket
import os

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
        # Recebe o comando ou nome do arquivo requisitado
        filename = client_socket.recv(2048).decode()
        
        # Se o cliente desconectar, encerra o loop
        if not filename:
            print(f'Cliente {client_address} desconectado.')
            break

        # Caso o cliente solicite a listagem de arquivos
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
        
        # Caso o cliente solicite um arquivo específico
        else:
            arquivo = filename
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
            else:
                print(f'O arquivo {arquivo} não foi encontrado no diretório {DIRETORIO}')
                client_socket.sendall(b'0')

    client_socket.close()
