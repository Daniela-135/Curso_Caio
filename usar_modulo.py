import meu_modulo as mm
# print(mm.soma(2,6))
# print(mm.saudacao('Daniela', 45))

# valor_a = int(input('Insira o primeiro valor:'))
# valor_b = int(input('Insira o segundo valor:'))

# print(mm.soma(valor_a, valor_b))

#em que ano você nasceu, em que ano estamos , qual a sua idade


usuarioNasc = int(input('\nInforme o ano que nasceu'))
usuariotual = int(input('\nInforme o ano atual'))
idade = mm.calcularIdade(usuarioNasc, usuariotual)
print(f'Você tem {idade} anos')
