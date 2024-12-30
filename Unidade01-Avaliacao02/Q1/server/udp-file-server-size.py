import socket 
import os  

server= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = "127.0.0.1" 
porta= 1234
server_address= (ip, porta)
DIRETORIO= 'files/'

server.bind(server_address) 

print(f'Servidor aguardando solicitações em {ip}:{porta}')
 
try: 
    filename, client_address = server.recvfrom(1024)
    filename= filename.decode() 

    path= os.path.join(DIRETORIO, filename)
    if os.path.isfile(path):
        tam=0
        with open(path, 'rb') as file:
            while True: 
                bloco = file.read(1024)
                if not 1024:
                        break 
                tam += len(bloco)
            print(f'Enviando o tamanho do arquivo {filename} ({tam} bytes ao cliente {client_address})')
            server.sendto(str(tam).encode(), client_address)
    else: 
         print(f'O arquivo {filename} não foi encontrado no diretório {DIRETORIO}')
         server.sendto(b'0', client_address)

except FileNotFoundError: 
    print(f'O arquivo solicitado {filename} não foi encontrado no servidor {server_address}')
            




        