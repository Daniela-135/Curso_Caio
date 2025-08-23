import pandas as pd

#carregar dados da planilha - 
caminho = 'C:\/Users\/sabado\/Desktop\/Python AD Daniela\/python_analise_dados-main\/01_base_vendas.xlsx'
df1 = pd.read_excel(caminho, sheet_name='Relatório de Vendas')
df2 = pd.read_excel(caminho, sheet_name='Relatório de Vendas1')

#exibir as primeiras linhas das tabelas
print('-------Primeiro Relatório---------')
print(df1.head())

print('-------Segundo Relatório---------')
print(df2.head())

# verficar se há duplicatas
print('Duplicatas norelatório 01')
print(df1.duplicated().sum())

print('Duplicatas norelatório 02')
print(df2.duplicated().sum())

#vamos consolidar as duas tabelas
print('Dados consolidados')
dfConsolidado =pd.concat([df1,df2] , ignore_index=True)
print(dfConsolidado.head())

#exibir o número de clientes por cidade
clientesPorCidade = dfConsolidado.groupby('Cidade')['Cliente'].nunique().sort_values(ascending=False)
print('Clientes por cidade')
print(clientesPorCidade)

# número de vendas por plano
vendasPorPlano = dfConsolidado['Plano Vendido'].value_counts()
print('Numero de vendas por Plano')
print(vendasPorPlano)


#exibir as 3 cidades com mais clientes:
top3Cidades = clientesPorCidade.head(3)
print('Top 3 Cidades')
print(top3Cidades)

#adicionar uma nova coluna - vamos classificar os planos como premium se for enterpreise os demais serão padrão
dfConsolidado['Status'] = dfConsolidado['plano Vendido'].apply(lambda x: 'Premium' if x =='Enterprise' else 'Padrão')

#exibir a distribuição dos status
statusDist = dfConsolidado['Status'].value_counts()
print(statusDist)

#Salvar a tabela em um arquivo novo
#Primeiro em Excel
dfConsolidado.to_excel('dados_consolidados.xlsx', index=False)
print('Dados salvos na planilha Excel')

#depois em csv
dfConsolidado.to_csv('dados_consolidados.csv', index=False)
print('Dados salvos na planilha csv')

#mensagem final
print('--------Programa Finalizado--------')