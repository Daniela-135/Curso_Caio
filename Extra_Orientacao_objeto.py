class Carro:
    def __int__(self, modelo, cor):
        #atributos do carro
        self.modelo = modelo
        self.cor = cor
        self.velocidade = 0
        self.ligado = False

    def acelerar(self, incremento):
        self.velocidade += incremento
        print(f'O {self.modelo} acelerou para {self.velocidade} Km/h')

    def desacelear(self, incremento):
        self.velocidade += incremento
        print(f'O {self.modelo} desacelerou para {self.velocidade} Km/h') 

   def parar(self, incremento):
        self.velocidade += incremento
        print(f'O {self.modelo} parou para {self.velocidade} Km/h')

   def reduzir_velocidade(self, incremento):
        while self.velocidade > 0:
             self.velocidade -= 5
             print(f'O {self.modelo} reduzou para{self.velocidade} Km/h')
        print(f'O {self.modelo} esta parado')
    
        


meu_carro = Carro('Fusca', 'Amarelo')

#criar o objeto carro
meu_carro = Carro('Fusca', 'Amarelo')
outro_carro = Carro('Creta','Prata')

meu_carro.acelerar(20)
meu_carro.acelerar(30)
outro_carro.acelerar(90)

