import socket

SERVER = '127.0.0.1' 
PORT = 1234 
DIRETORIO = "files/"

tcpSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcpSock.connect((SERVER, PORT))

# Loop para iterar o pedido do arquivo. 
while True:
    nomeArq = input("Digite o comando desejado ou digite 0 para sair: ") # Input para receber o nome do arquivo.
    if nomeArq == "0": # Caso seja digitado 0, a conexão com o servidor é fechado e o loop é encerrado.
        tcpSock.close()
        print("Encerrando programa...")
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
        arquivo = input("Digite o nome do arquivo solicitado: \n")

        print ("Enviando pedido a", (SERVER, PORT), "para", arquivo) # Caso seja pedido um arquivo, será printado o nome em si ao servidor conectado.
        tcpSock.send(arquivo.encode('utf-8')) # Enviará o pedido codificado em UTF-8.

        dataTam = tcpSock.recv(2048) # Pacote contendo o tamanho do arquivo solicitado.

        try:
            tamArq = int(dataTam.decode('utf-8')) # Transforma o pacote contendo o tamanho em inteiro e printa o nome e tamanho.
            print(f"O arquivo '{arquivo}' possui o tamanho de {tamArq} Bytes.")
        except ValueError: # Caso o valor recebido seja 0, dará essa exceção.
            continue

        if tamArq > 0: # Se o valor recebido for maior que 0, criará um arquivo vazio com o mesmo nome no diretório.
            print("Salvando o arquivo localmente...")
            with open(DIRETORIO+arquivo, "wb") as fd:
                recebido = 0 # varíavel para receber o tamanho do arquivo.
                while recebido < tamArq:
                    data = tcpSock.recv(4096) # Será recebido mais um bloco de bytes contendo o arquivo em si e será escrito até o loop ser encerrado.
                    fd.write(data)
                    print("lidos: ", len(data), "Bytes") # Printa quantos bytes foram recebidos e lidos.
                    recebido += len(data)
                print(f"O arquivo '{arquivo}' foi recebido com sucesso")
        
        else:
            print("Erro: Arquivo desejado não existe ou não foi encotrado.") # Caso o valor recebido seja 0, dará o erro.

        tcpSock.close() # A conexão com o servidor é fechado e o loop é encerrado.
        break