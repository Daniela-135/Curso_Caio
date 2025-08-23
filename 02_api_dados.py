#https://servicodados.ibge.gov.br/api/v2/censos/nomes/daniela
import json, requests

nome = input('Escreva o Nome a ser Buscado')
resposta = requests.get('https://servicodados.ibge.gov.br/api/v2/censos/nomes/{no Fme}')
jsonDados = json.loads(resposta.text)
print(jsonDados[0]['res'])
