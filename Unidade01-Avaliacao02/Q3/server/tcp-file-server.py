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

    # Recebe o comando ou nome do arquivo requisitado
    filename= client_socket.recv(2048).decode()  # Buffer de até 2048 bytes

# Caso o Servidor receba como solicitação do cliente "1", o cliente solicita a listagem dos arquivos no servidor 
    if filename == "1": 
        # Listar arquivos no diretório
        print(f'Recebida solicitação de listagem de arquivos do cliente {client_address}')
        list_arq = os.listdir(DIRETORIO) # Armazena os arquivos presentes no diretório
        listagem = []
        for file in list_arq: 
            file_path = os.path.join(DIRETORIO, file) # Constroi o caminho completo para o arquivo
            if os.path.isfile(file_path): 
                file_size = os.path.getsize(file_path) # Tamanho do arquivo em bytes 
                listagem.append(f"{file} ({file_size} bytes)")
        if listagem:
            client_socket.sendall("\n".join(listagem).encode()) # Envio da listagem em bytes para o cliente 
        else:
            client_socket.sendall(b''(str(f'Não foi possível encontrar os arquivos em {DIRETORIO}')))

# Caso ele queira apenas a requisição de um único arquivo
    else:
        arquivo = filename
        path = os.path.join(DIRETORIO, arquivo)

        # Verifica se o arquivo existe no diretório
        if os.path.isfile(path):
            tam = os.path.getsize(path)  # Obtém o tamanho do arquivo
            print(f'Enviando o tamanho do arquivo {arquivo} ({tam} bytes) ao cliente {client_address}')
            client_socket.sendall(str(tam).encode())  # Envia o tamanho do arquivo

            # Leitura do arquivo e envio dos dados em blocos de 2048 bytes
            with open(path, 'rb') as file:
                while chunk := file.read(2048):  
                    client_socket.sendall(chunk)
            print(f'Arquivo {arquivo} enviado com sucesso para {client_address}')

        else:
            # Caso o arquivo não seja encontrado, envia '0' ao cliente
            print(f'O arquivo {arquivo} não foi encontrado no diretório {DIRETORIO}')
            client_socket.sendall(b'0')

    client_socket.close()  
