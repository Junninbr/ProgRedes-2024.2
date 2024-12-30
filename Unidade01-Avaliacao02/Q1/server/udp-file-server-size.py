import socket 

server= socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
ip = "192.168.1.6" 
porta= 65432 
server_address= (ip, porta)

server.bind(server_address) 

print(f'Servidor aguardando solicitações em {ip}:{porta}')

while True: 
    filename, client_address = server.recvfrom(1024)
    filename= filename.decode 

    if filename: 
        try: 
            with open (filename, 'rb') as file: 
                file.seek(0, 2)
                tam = file.tell()
            print(f'Enviando o tamanho do arquivo {filename } ({tam} bytes) ao cliente {client_address}')
            server.sendto(str(tam).encode(), client_address)
        
        except FileNotFoundError: 
            print(f'O arquivo solicitado {filename} não foi encontrado no servidor {server_address}')
            
    else: 
        print(f'Nenhum arquivo foi solicitado pelo cliente {client_address}')
        server.sendto(b'Nenhum arquivo especificado!', client_address)