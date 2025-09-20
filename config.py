



# configurações comuns do sistema

FOLDER = "C:/Users/sabado/Desktop/Python AD Daniela/python_analise_dados-main/AIS/"
DB_PATH = 'BANCODEDADOSais.DB'
FLASK_DEBUG =  True
FLASK_HOST = '127.0.0.1'
FLASK_PORT = 5000

## Rotas comuns do sistema
ROTAS = [
    '/',                            #rota 00
    '/upload',                      #rota 01
    '/consultar',                   #rota 02
    '/graficos',                    #rota 03
    '/editar_inadimplencia',        #rota 04
    '/corelação'                    #rota 05
    ]