import socket

SERVER = '192.168.1.6'
PORT = 3456
DIRETORIO = "files/"

udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

while True:
    nomeArq = input("Digite o nome do arquivo desejado: ")

    print ("Enviando pedido a", (SERVER, PORT), "para", nomeArq)
    udpSock.sendto(nomeArq.encode('utf-8'), (SERVER, PORT))

    dataTam, source = udpSock.recvfrom(1024)
    try:
        tamArq = int(dataTam.decode('utf-8'))
    except ValueError:
        print("Erro: Não foi possível receber o tamanho do arquivo ou não foi encontrado.")
        continue

    if tamArq > 0:
        print("Salvando o arquivo localmente...")
        with open(DIRETORIO+nomeArq, "wb") as fd:
            recebido = 0
            while recebido < tamArq:
                data, source = udpSock.recvfrom(4096)
                fd.write(data)
                print("lidos: ", len(data))
                recebido += len(data)
            print(f"O arquivo {nomeArq} foi recebido com sucesso")
    
    else:
        print("Erro: Arquivo desejado não existe ou não foi encotrado.")

udpSock.clos