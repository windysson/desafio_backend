   
import requests, time

# Defina o caminho do arquivo CSV
caminho_arquivo = './input.csv'

# URL da API no servidor remoto
print("inicado a requisição")
url = 'http://127.0.0.1:8000/boletos/processar-arquivo/'

# Fazendo a requisição POST com o arquivo
with open(caminho_arquivo, 'rb') as arquivo:
    arquivos = {'file': arquivo}
    init = time.time()
    resposta = requests.post(url, files=arquivos)
    print(time.time() - init)

# Exibindo a resposta da API
if resposta.status_code == 200:
    print('Sucesso:', resposta.json())
else:
    print('Erro:', resposta.status_code, resposta.text)
