import socket 
import os  

server= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = "127.0.0.1" 
porta= 1234
server_address= (ip, porta)
DIRETORIO= 'files/'

server.bind(server_address) 

print(f'Servidor escutando em.... {ip}:{porta}')
 
try:
    while True:
        # Recebe o nome do arquivo requisitado
        filename, client_address = server.recvfrom(2048) # Buffer de até 2048 bytes
        filename = filename.decode() 
        path = os.path.join(DIRETORIO, filename)
        
        # Verifica se o arquivo existe no diretório
        if os.path.isfile(path):
            tam = os.path.getsize(path) # Consegue o tamanho do arquivo 
            print(f'Enviando o tamanho do arquivo {filename} ({tam} bytes) ao cliente {client_address}') 
            server.sendto(str(tam).encode(), client_address) # Envio do tamanho do arquivo como string codificada em bytes ao cliente 

        # Leitura do arquivo e o envio dos dados em blocos de 2048 bytes
            with open(path, 'rb') as file:
                while chunk := file.read(2048): # Enquanto o arquivo não tiver chegado ao final, leia o próximo bloco de 2048 bytes
                    server.sendto(chunk, client_address)
            print(f'Arquivo {filename} enviado com sucesso para {client_address}') # Envia o bloco ao cliente
        else:
            # Caso o arquivo não for encontrado ele enia '0' ao cliente
            print(f'O arquivo {filename} não foi encontrado no diretório {DIRETORIO}')
            server.sendto(b'0', client_address)

except Exception as e:
    print(f"Erro no servidor: {e}")
finally:
    server.close()
            




        
