import os

class analisadorSintatico:
    def __init__(self, tokens):
        self.tokens = tokens
        self.token_atual_index = 0
        self.erros_sintaticos = []
        self.fim_tokens = False

    #Método para consumir o token atual e verificar se é o token esperado
    def eat(self, token_esperado, analisar_tipo = 0):
        cont = 0
        if analisar_tipo == 0:
            while self.token_atual_index <= len(self.tokens) - 1 and self.token_atual()[2].strip() not in token_esperado:
                if cont == 0:
                    self.error(token_esperado)
                self.token_atual_index += 1
                cont += 1
        else:
            while self.token_atual_index <= len(self.tokens) - 1 and self.token_atual()[1] not in token_esperado:
                if cont == 0:
                    self.error(token_esperado)
                self.token_atual_index += 1
                cont += 1
        
        self.update_token_index()

    #Método para ir para o próximo token
    def update_token_index(self):
        self.token_atual_index += 1
        if self.token_atual_index >= len(self.tokens):
            self.fim_tokens = True
            self.token_atual_index = len(self.tokens) - 1

    #Método para retornar o token atual
    def token_atual(self):
        return self.tokens[self.token_atual_index].split(" ")
    
    #Método para retornar o token anterior
    def token_anterior(self):
        if self.token_atual_index != 0:
            return self.tokens[self.token_atual_index-1].split(" ")
        return self.tokens[self.token_atual_index].split(" ")

    #Método para salvar os erros sintáticos
    def error(self, token_esperado):
        if not self.fim_tokens:
            if len(token_esperado) > 1:
                self.erros_sintaticos.append('Erro na linha ' + self.token_atual()[0] + ' (esperado "'+ ' || '.join(token_esperado) + '" porem encontrou "' + self.token_atual()[2].strip() +
                                        '" do tipo {' + self.token_atual()[1] + '}).')
            else:
                self.erros_sintaticos.append('Erro na linha ' + self.token_atual()[0] + ' (esperado "'+ ''.join(token_esperado) + '" porem encontrou "' + self.token_atual()[2].strip() +
                                        '" do tipo {' + self.token_atual()[1] + '}).')

    #Método para iniciar a análise sintática
    def startAnalisador(self):
        self.programa()

    #Método da análise do corpo 'algoritmo'
    def programa(self):
        self.eat(['algoritmo'])
        self.eat(['{'])
        if self.token_atual()[2].strip() == 'constantes':
            self.constantes()
        if self.token_atual()[2].strip() == 'variaveis':
            self.variaveis()
        if self.token_atual()[2].strip() == 'registro':
            self.registro()
        while self.token_atual()[2].strip() == 'funcao':
            self.funcao()
        self.principal()
        self.eat(['}'])

    #Método da análise do corpo de 'constantes'
    def constantes(self):
        self.eat(['constantes'])
        self.eat(['{'])
        while self.token_atual()[2].strip() != '}':
            self.declaracao_const()
        self.eat(['}'])

    #Método da análise da declaração de constantes
    def declaracao_const(self):
        self.eat(['inteiro', 'real', 'booleano', 'char', 'cadeia'])
        self.eat(['IDE'], 1)
        self.eat(['='])
        self.expressao()
        while self.token_atual()[2].strip() == ',':
            self.eat([','])
            self.eat(['IDE'], 1)
            self.eat(['='])
            self.expressao()
        self.eat([';'])

    #Método da análise do corpo 'variaveis'
    def variaveis(self):
        self.eat(['variaveis'])
        self.eat(['{'])
        while self.token_atual()[2].strip() != '}':
            self.declaracao_var()
        self.eat(['}'])


    #Método da análise da declaração de variáveis
    def declaracao_var(self):
        cont = 0
        while self.token_atual()[2].strip() not in ('inteiro', 'real', 'booleano', 'char', 'cadeia') and self.token_atual()[1] != 'IDE' and self.fim_tokens == False:
            if cont == 0:
                self.error(['inteiro || real || booleano || char || cadeia || registro'])
            self.update_token_index()
            cont += 1
        self.eat([self.token_atual()[2].strip()])
        self.eat(['IDE'], 1)
        if self.token_atual()[2].strip() == '[':
            self.declaracao_vetor()
        while self.token_atual()[2].strip() == ',':
            self.eat([','])
            self.eat(['IDE'], 1)
            if self.token_atual()[2].strip() == '[':
                self.declaracao_vetor()
        self.eat([';'])

    #Método da análise do corpo 'registro'
    def registro(self):
        self.eat(['registro'])
        self.eat(['IDE'], 1)
        self.eat(['{'])
        while self.token_atual()[2].strip() != '}':
            self.eat(['inteiro', 'real', 'booleano', 'char', 'cadeia'])
            self.eat(['IDE'], 1)
            if self.token_atual()[2].strip() == '[':
                self.declaracao_vetor()
            while self.token_atual()[2].strip() == ',':
                self.eat([','])
                self.eat(['IDE'], 1)
                if self.token_atual()[2].strip() == '[':
                    self.declaracao_vetor()
            self.eat([';'])
        self.eat(['}'])

    #Método da análise do corpo 'principal'
    def principal(self):
        self.eat(['principal'])
        self.eat(['('])
        self.eat([')'])
        self.eat(['{'])
        self.escopo(True)
        self.eat(['}'])

    #Método da análise de expressão geral
    def expressao(self, permitir_nulo = False):
        cont = 0
        cont1 = 0
        cont2 = 0
        while self.token_atual()[2].strip() not in (';', ']', ',', ')') and self.token_atual()[1] != 'REL' and self.fim_tokens == False:
            cont += 1

            #Consumindo o operador
            if cont != 1:
                while self.fim_tokens == False and (self.token_atual()[1] not in ('ART', 'LOG') or self.token_atual()[2].strip() in ('++', '--', '!')):
                    if cont2 == 0:
                        self.error(['ART || LOG com excecao de: ++, --, !'])
                    self.update_token_index()
                    cont2 += 1
                self.eat([self.token_atual()[2].strip()])
                cont2 = 0
            
            #Consumindo o ''valor'' após o operador
            while self.token_atual()[1] not in ('NRO', 'IDE', 'CAC') and self.token_atual()[2].strip() not in ('falso', 'verdadeiro', '!', '(') and self.fim_tokens == False:
                if cont1 == 0:
                    self.error(['NRO || IDE || CAC || falso || verdadeiro'])
                self.update_token_index()
                cont1 += 1
            cont1 = 0
            self.eat([self.token_atual()[2].strip()])
            if self.token_anterior()[1] == 'IDE':
                if self.token_atual()[2].strip() == '.':
                    self.eat(['.'])
                    self.eat(['IDE'], 1)
                    if self.token_atual()[2].strip() == '[':
                        self.eat(['['])
                        self.eat(['NRO'], 1)
                        self.eat([']'])
                        if self.token_atual()[2].strip() == '[':
                            self.eat(['['])
                            self.eat(['NRO'], 1)
                            self.eat([']'])
                elif self.token_atual()[2].strip() == '(':
                    self.eat(['('])
                    self.expressao(True)
                    while self.token_atual()[2].strip() == ',' and self.token_anterior()[2].strip() != '(':
                        self.eat([','])
                        self.expressao()
                    self.eat([')'])
                elif self.token_atual()[2].strip() == '[':
                    self.eat(['['])
                    self.eat(['NRO'], 1)
                    self.eat([']'])
                    if self.token_atual()[2].strip() == '[':
                        self.eat(['['])
                        self.eat(['NRO'], 1)
                        self.eat([']'])
            
            elif self.token_anterior()[2].strip() == '!':
                self.eat(['IDE'], 1)
                if self.token_atual()[2].strip() == '.':
                    self.eat(['.'])
                    self.eat(['IDE'], 1)
                    if self.token_atual()[2].strip() == '[':
                        self.eat(['['])
                        self.eat(['NRO'], 1)
                        self.eat([']'])
                        if self.token_atual()[2].strip() == '[':
                            self.eat(['['])
                            self.eat(['NRO'], 1)
                            self.eat([']'])
                elif self.token_atual()[2].strip() == '(':
                    self.eat(['('])
                    self.expressao(True)
                    while self.token_atual()[2].strip() == ',' and self.token_anterior()[2].strip() != '(':
                        self.eat([','])
                        self.expressao()
                    self.eat([')'])
                elif self.token_atual()[2].strip() == '[':
                    self.eat(['['])
                    self.eat(['NRO'], 1)
                    self.eat([']'])
                    if self.token_atual()[2].strip() == '[':
                        self.eat(['['])
                        self.eat(['NRO'], 1)
                        self.eat([']'])
            
            elif self.token_anterior()[2].strip() == '(':
                self.expressao()
                self.eat([')'])


        if cont == 0 and permitir_nulo == False:
            self.error(['Valor ou expressao'])

    #Método da análise da declaração de vetores e matrizes
    def declaracao_vetor(self):
        self.eat(['['])
        self.eat(['NRO'], 1)
        self.eat([']'])
        if self.token_atual()[2].strip() == '[':
            self.eat(['['])
            self.eat(['NRO'], 1)
            self.eat([']'])
    
    #Método da análise da definição de uma função
    def funcao(self):
        self.eat(['funcao'])
        if self.token_atual()[2].strip() in ('inteiro', 'real', 'booleano', 'char', 'cadeia', 'vazio'):
            self.eat(['inteiro', 'real', 'booleano', 'char', 'cadeia', 'vazio'])
        else:
            self.eat(['IDE'], 1)
        self.eat(['IDE'], 1)
        self.eat(['('])
        if self.token_atual()[1] in ['IDE', 'PRE']:
            self.eat(['inteiro', 'real', 'booleano', 'char', 'cadeia'])
            self.eat(['IDE'], 1)
            if self.token_atual()[2].strip() == '[':
                self.eat(['['])
                self.eat(['NRO'], 1)
                self.eat([']'])
                if self.token_atual()[2].strip() == '[':
                    self.eat(['['])
                    self.eat(['NRO'], 1)
                    self.eat([']'])
            while self.token_atual()[2].strip() == ',':
                self.eat([','])
                self.eat(['inteiro', 'real', 'booleano', 'char', 'cadeia'])
                self.eat(['IDE'], 1)
                if self.token_atual()[2].strip() == '[':
                    self.eat(['['])
                    self.eat(['NRO'], 1)
                    self.eat([']'])
                    if self.token_atual()[2].strip() == '[':
                        self.eat(['['])
                        self.eat(['NRO'], 1)
                        self.eat([']'])
        self.eat([')'])
        self.eat(['{'])
        if self.token_atual()[2].strip() == 'variaveis':
            self.variaveis()
        self.escopo(True)
        self.eat(['retorno'])
        self.expressao(True)
        self.eat([';'])
        self.eat(['}'])

    #Método da análise do ''leia()''
    def leia(self):
        self.eat(['leia'])
        self.eat(['('])
        self.eat(['IDE'], 1)
        if self.token_atual()[2].strip() == '.':
            self.eat(['.'])
            self.eat(['IDE'], 1)
            if self.token_atual()[2].strip() == '[':
                self.eat(['['])
                self.eat(['NRO'], 1)
                self.eat([']'])
                if self.token_atual()[2].strip() == '[':
                    self.eat(['['])
                    self.eat(['NRO'], 1)
                    self.eat([']'])
        elif self.token_atual()[2].strip() == '[':
            self.eat(['['])
            self.eat(['NRO'], 1)
            self.eat([']'])
            if self.token_atual()[2].strip() == '[':
                self.eat(['['])
                self.eat(['NRO'], 1)
                self.eat([']'])
        self.eat([')'])
        self.eat([';'])
    
    #Método da análise do ''escreva()''
    def escreva(self):
        self.eat(['escreva'])
        self.eat(['('])
        self.eat(['IDE', 'NRO', 'CAC'], 1)
        if self.token_anterior()[1] == 'IDE':
            if self.token_atual()[2].strip() == '.':
                self.eat(['.'])
                self.eat(['IDE'], 1)
                if self.token_atual()[2].strip() == '[':
                    self.eat(['['])
                    self.eat(['NRO'], 1)
                    self.eat([']'])
                    if self.token_atual()[2].strip() == '[':
                        self.eat(['['])
                        self.eat(['NRO'], 1)
                        self.eat([']'])
            elif self.token_atual()[2].strip() == '[':
                self.eat(['['])
                self.eat(['NRO'], 1)
                self.eat([']'])
                if self.token_atual()[2].strip() == '[':
                    self.eat(['['])
                    self.eat(['NRO'], 1)
                    self.eat([']'])
        self.eat([')'])
        self.eat([';'])

    #Método da análise do ''enquanto()''
    def enquanto(self):
        cont = 0
        self.eat(['enquanto'])
        self.eat(['('])
        self.expressao()
        while self.token_atual()[1] != 'REL' or self.token_atual()[2].strip() == '=':
            if cont == 0:
                self.error(['REL com excecao de: ='])
            self.update_token_index()
            cont += 1
        self.eat(['REL'], 1)
        self.expressao()
        self.eat([')'])
        self.eat(['{'])
        self.escopo()
        self.eat(['}'])
    
    #Método da análise do ''se()''
    def se(self):
        self.eat(['se'])
        self.eat(['('])
        self.expressao()
        self.eat([')'])
        self.eat(['{'])
        self.escopo()
        self.eat(['}'])
        if self.token_atual()[2].strip() == 'senao':
            self.senao()
    
    #Método da análise do ''senao''
    def senao(self):
        self.eat(['senao'])
        self.eat(['{'])
        self.escopo()
        self.eat(['}'])
    
    #Método da análise de escopo
    def escopo(self, permitir_nulo = False):
        cont = 0
        while self.token_atual()[2].strip() != '}' and self.token_atual()[2].strip() != 'retorno':
            if self.token_atual()[1] == 'IDE':
                cont = 0
                self.eat(['IDE'], 1)
                if self.token_atual()[2].strip() == '.':
                    self.eat(['.'])
                    self.eat(['IDE'], 1)
                    if self.token_atual()[2].strip() == '[':
                        self.eat(['['])
                        self.eat(['NRO'], 1)
                        self.eat([']'])
                        if self.token_atual()[2].strip() == '[':
                            self.eat(['['])
                            self.eat(['NRO'], 1)
                            self.eat([']'])
                    #Atribuição
                    self.eat(['='])
                    self.expressao()
                    self.eat([';'])
                elif self.token_atual()[2].strip() == '[':
                    self.eat(['['])
                    self.eat(['NRO'], 1)
                    self.eat([']'])
                    if self.token_atual()[2].strip() == '[':
                        self.eat(['['])
                        self.eat(['NRO'], 1)
                        self.eat([']'])
                    #Atribuição
                    self.eat(['='])
                    self.expressao()
                    self.eat([';'])
                #Chamada de função
                elif self.token_atual()[2].strip() == '(':
                    self.eat(['('])
                    self.expressao(True)
                    while self.token_atual()[2].strip() == ',' and self.token_anterior()[2].strip() != '(':
                        self.eat([','])
                        self.expressao()
                    self.eat([')'])
                    self.eat([';'])
                elif self.token_atual()[2].strip() == '=':
                    self.eat(['='])
                    self.expressao()
                    self.eat([';'])
            elif self.token_atual()[2].strip() == 'se':
                cont = 0
                self.se()
            elif self.token_atual()[2].strip() == 'enquanto':
                cont = 0
                self.enquanto()
            elif self.token_atual()[2].strip() == 'leia':
                cont = 0
                self.leia()
            elif self.token_atual()[2].strip() == 'escreva':
                cont = 0
                self.escreva()
            else:
                if cont == 0:
                    self.error(['Reatribuicao || Chamada de funcao || se || enquanto || leia || escreva'])
                self.update_token_index()
                cont += 1
        
        if cont == 0 and permitir_nulo == False and self.token_anterior()[2].strip() == '{':
            self.error(['Reatribuicao || Chamada de funcao || se || enquanto || leia || escreva'])

def estados (estado_atual, caractere, lexema, ultimo_token):
    palavras_reservadas = ["algoritmo", "principal", "variaveis", "constantes",
                           "registro", "funcao", "retorno", "vazio", "se", "senao",
                           "enquanto", "leia", "escreva", "inteiro", "real", "booleano", "char", "cadeia", "verdadeiro", "falso"]
    delimitadores = [';', ',', '.', '(', ')', '[', ']', '{', '}']

    #Estado inicial
    if estado_atual == 0:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
        elif caractere.isspace():
            pass
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
        else:
            lexema += caractere
            estado_atual = 5
    
    #Estado com possibilidade de palavras reservadas ou identificadores
    elif estado_atual == 1:
        if caractere.isalpha() or caractere == '_' and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 1
        elif caractere == '&':
            lexema += caractere
            estado_atual = 22
        elif caractere == '|':
            lexema += caractere
            estado_atual = 25
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            if lexema[:len(lexema)-1] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            if lexema[:len(lexema)-1] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            if lexema[:len(lexema)-1] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            if lexema[:len(lexema)-1] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            if lexema[:len(lexema)-1] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            if lexema[:len(lexema)-1] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            if lexema[:len(lexema)-1] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            if lexema[:len(lexema)-1] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            if lexema[:len(lexema)-1] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 7
    
    #Estado dos numeros
    elif estado_atual == 2:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 28
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
        elif caractere == '.':
            lexema += caractere
            estado_atual = 33
        elif caractere == '&':
            lexema += caractere
            estado_atual = 35
        elif caractere == '|':
            lexema += caractere
            estado_atual = 36
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'NRO', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'NRO', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'NRO', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'NRO', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'NRO', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'NRO', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'NRO', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'NRO', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'NRO', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 28

    #Estado com possibilidade de operadores relacionais ou operador lógico
    elif estado_atual == 3:
        if caractere == '=':
            lexema += caractere
            estado_atual = 4
        elif caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'REL' , lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'REL' , lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'REL' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'REL' , lexema, estado_atual
        elif caractere == '<' or caractere == '>':
            lexema += caractere
            estado_atual = 3
            return 'REL' , lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'REL' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'REL' , lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'REL' , lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'REL' , lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'REL' , lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'REL' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'REL' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'REL' , lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'REL' , lexema, estado_atual
    
    #Estado final dos operadores relacionais ==, <= e >=
    elif estado_atual == 4:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'REL' , lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'REL' , lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'REL' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'REL' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'REL' , lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'REL' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'REL' , lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'REL' , lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'REL' , lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'REL' , lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'REL' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'REL' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'REL' , lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'REL' , lexema, estado_atual
    
    #Estado final do token mal formado
    elif estado_atual == 5:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'TMF', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'TMF', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 37
        elif caractere == '|':
            lexema += caractere
            estado_atual = 38
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'TMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'TMF' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'TMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'TMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'TMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'TMF' , lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'TMF' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'TMF' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'TMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
    
    #Estado dos delimitadores
    elif estado_atual == 6:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'DEL', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'DEL', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'DEL' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'DEL' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'DEL', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'DEL' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'DEL', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'DEL', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'DEL', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'DEL' , lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'DEL' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'DEL' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'DEL', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'DEL', lexema, estado_atual
    
    #Estado de identificador mal formado
    elif estado_atual == 7:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 7
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 7
        elif caractere == '&':
            lexema += caractere
            estado_atual = 31
        elif caractere == '|':
            lexema += caractere
            estado_atual = 32
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'IMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'IMF' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'IMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'IMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'IMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'IMF' , lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'IMF' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'IMF' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'IMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 7
    
    #Estado para identificar se é um comentario de linha, operador aritmetico ou comentario de bloco
    elif estado_atual == 8:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'ART', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'ART', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'ART' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'ART' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'ART', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'ART' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'ART', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'ART', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 9
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'ART' , lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'ART' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 26
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'ART', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'ART', lexema, estado_atual
    
    #Estado final de um comentário de linha
    elif estado_atual == 9:
        pass

    #Estado da cadeia de caracteres
    elif estado_atual == 10:
        if caractere == '"':
            lexema += caractere
            estado_atual = 11
        elif ord(caractere) >= 32 and ord(caractere) <= 126:
            lexema += caractere
        else:
            lexema += caractere
            estado_atual = 12
    
    #Estado final da cadeia de caracteres
    elif estado_atual == 11:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'CAC', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'CAC', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'CAC' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'CAC' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'CAC', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'CAC' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'CAC', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'CAC', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'CAC', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'CAC' , lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'CAC' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'CAC' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'CAC', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'CAC', lexema, estado_atual
    
    #Estado de cadeia de caracteres mal formado
    elif estado_atual == 12:
        if caractere == '"':
            lexema += caractere
            estado_atual = 13
        else:
            lexema += caractere

    #Estado final de cadeia de caracteres mal formado
    elif estado_atual == 13:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'CMF', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'CMF', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'CMF' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'CMF' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'CMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'CMF' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'CMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'CMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'CMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'CMF' , lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'CMF' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'CMF' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'CMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'CMF', lexema, estado_atual

    #Estado de operador aritmetico + ou ++
    elif estado_atual == 14:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'ART', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'ART', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'ART' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'ART' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'ART', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'ART' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'ART', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'ART', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'ART', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 15
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'ART' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'ART' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'ART', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'ART', lexema, estado_atual
    
    #Estado final de operador aritmetico ++
    elif estado_atual == 15:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'ART', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'ART', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'ART' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'ART' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'ART', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'ART' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'ART', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'ART', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'ART', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'ART', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'ART' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'ART' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'ART', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'ART', lexema, estado_atual
    
    #Estado de operador aritmetico - ou --
    elif estado_atual == 16:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'ART', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            if not (ultimo_token == 'STARTLINE' or ultimo_token == 'ART' or ultimo_token == 'REL' or ultimo_token == 'LOG'):
                return 'ART', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'ART' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'ART' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'ART', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'ART' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'ART', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'ART', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'ART', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'ART', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 17
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'ART' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'ART', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'ART', lexema, estado_atual
    
    #Estado final de operador aritmetico --
    elif estado_atual == 17:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'ART', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'ART', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'ART' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'ART' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'ART', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'ART' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'ART', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'ART', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'ART', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'ART', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'ART', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'ART' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'ART', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'ART', lexema, estado_atual

    #Estado de operador aritmetico *
    elif estado_atual == 18:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'ART', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'ART', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'ART' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'ART' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'ART', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'ART' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'ART', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'ART', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'ART', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'ART', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'ART', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'ART', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'ART', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'ART', lexema, estado_atual
    
    #Estado de operador logico !
    elif estado_atual == 19:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'LOG', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'LOG', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'LOG' , lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'LOG' , lexema, estado_atual
        elif caractere == '<' or caractere == '>':
            lexema += caractere
            estado_atual = 3
            return 'LOG', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'LOG' , lexema, estado_atual
        elif caractere == '=':
            lexema += caractere
            estado_atual = 4
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'LOG', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'LOG', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'LOG', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'LOG', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'LOG', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'LOG', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'LOG', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'LOG', lexema, estado_atual
    
    #Estado de token mal formado para &
    elif estado_atual == 20:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'TMF', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'TMF', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 21
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'TMF' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'TMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'TMF' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'TMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'TMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'TMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'TMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'TMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'TMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'TMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'TMF', lexema, estado_atual
    
    #Estado de operador logico &&
    elif estado_atual == 21:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'LOG', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'LOG', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'LOG', lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'LOG' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'LOG', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'LOG' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'LOG', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'LOG', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'LOG', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'LOG', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'LOG', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'LOG', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'LOG', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'LOG', lexema, estado_atual
    
    #Estado de IDE ou PRE seguido de LOG, ou IMF -> para &
    elif estado_atual == 22:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 7
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 7
        elif caractere == '&':
            lexema += caractere
            estado_atual = 21
            if lexema[:len(lexema)-2] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'IMF' , lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'IMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'IMF', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'IMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'IMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'IMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'IMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'IMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'IMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'IMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'IMF', lexema, estado_atual
    
    #Estado de token mal formado para |
    elif estado_atual == 23:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'TMF', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'TMF', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'TMF', lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 24
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'TMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'TMF' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'TMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'TMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'TMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'TMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'TMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'TMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'TMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'TMF', lexema, estado_atual
    
    #Estado de operador logico ||
    elif estado_atual == 24:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'LOG', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'LOG', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'LOG', lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 23
            return 'LOG', lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'LOG', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'LOG' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'LOG', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'LOG', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'LOG', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'LOG', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'LOG', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'LOG', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'LOG', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'LOG', lexema, estado_atual
    
    #Estado de IDE ou PRE seguido de LOG, ou IMF -> para &
    elif estado_atual == 25:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 7
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 7
        elif caractere == '&':
            lexema += caractere
            estado_atual = 20
            return 'IMF', lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 24
            if lexema[:len(lexema)-2] in palavras_reservadas:
                return 'PRE', lexema, estado_atual
            else:
                return 'IDE', lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'IMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'IMF', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'IMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'IMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'IMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'IMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'IMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'IMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'IMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
            return 'IMF', lexema, estado_atual
    
    #Estado do comentario em bloco
    elif estado_atual == 26:
        lexema += caractere
        if caractere == '*':
            estado_atual = 27
    
    #Estado final do comentario em bloco
    elif estado_atual == 27:
        lexema += caractere
        if caractere == '/':
            estado_atual = 0
            lexema = ''
        elif caractere == '*':
            estado_atual = 27
        else:
            estado_atual = 26
    
    #Estado de numero mal formado
    elif estado_atual == 28:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 28
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 28
        elif caractere == '&':
            lexema += caractere
            estado_atual = 29
        elif caractere == '|':
            lexema += caractere
            estado_atual = 30
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'NMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'NMF', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'NMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'NMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'NMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'NMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'NMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'NMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'NMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 28
    
    #Estado de numero mal formado com possibilidade de ser seguido por &&
    elif estado_atual == 29:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 28
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 28
        elif caractere == '&':
            lexema += caractere
            estado_atual = 21
            return 'NMF', lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 30
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'NMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'NMF', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'NMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'NMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'NMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'NMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'NMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'NMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'NMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 28
    
    #Estado de numero mal formado com possibilidade de ser seguido por ||
    elif estado_atual == 30:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 28
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 28
        elif caractere == '&':
            lexema += caractere
            estado_atual = 29
        elif caractere == '|':
            lexema += caractere
            estado_atual = 24
            return 'NMF', lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'NMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'NMF', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'NMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'NMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'NMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'NMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'NMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'NMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'NMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 28
    
    #Estado de identificador mal formado com possibilidade de ser seguido por &&
    elif estado_atual == 31:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 7
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 7
        elif caractere == '&':
            lexema += caractere
            estado_atual = 21
            return 'IMF', lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 32
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'IMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'IMF' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'IMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'IMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'IMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'IMF' , lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'IMF' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'IMF' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'IMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 7
    
    #Estado de identificador mal formado com possibilidade de ser seguido por ||
    elif estado_atual == 32:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 7
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 7
        elif caractere == '&':
            lexema += caractere
            estado_atual = 31
        elif caractere == '|':
            lexema += caractere
            estado_atual = 24
            return 'IMF', lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'IMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'IMF' , lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'IMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'IMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'IMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'IMF' , lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'IMF' , lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'IMF' , lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'IMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 7
    
    #Estado dos numeros de ponto flutuante
    elif estado_atual == 33:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 28
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 34
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'NMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 28
    
    #Estado final de numero de ponto flutuante
    elif estado_atual == 34:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 28
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 34
        elif caractere == '.':
            lexema += caractere
            estado_atual = 28
        elif caractere == '&':
            lexema += caractere
            estado_atual = 35
        elif caractere == '|':
            lexema += caractere
            estado_atual = 36
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'NRO', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'NRO', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'NRO', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'NRO', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'NRO', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'NRO', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'NRO', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'NRO', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'NRO', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 28
    
    #Estado de numero de ponto flutuante com possibilidade de ser seguido por &&
    elif estado_atual == 35:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 28
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 28
        elif caractere == '&':
            lexema += caractere
            estado_atual = 21
            return 'NRO', lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 30
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'NMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'NMF', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'NMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'NMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'NMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'NMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'NMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'NMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'NMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 28
    
    #Estado de numero de ponto flutuante com possibilidade de ser seguido por ||
    elif estado_atual == 36:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 28
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 28
        elif caractere == '&':
            lexema += caractere
            estado_atual = 29
        elif caractere == '|':
            lexema += caractere
            estado_atual = 24
            return 'NRO', lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'NMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'NMF', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'NMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'NMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'NMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'NMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'NMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'NMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'NMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 28
    
    #Estado de TMF com possibilidade de ser seguido por &&
    elif estado_atual == 37:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'TMF', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'TMF', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 21
            return 'TMF', lexema, estado_atual
        elif caractere == '|':
            lexema += caractere
            estado_atual = 38
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'TMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'TMF', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'TMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'TMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'TMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'TMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'TMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'TMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'TMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
    
    #Estado de TMF com possibilidade de ser seguido por ||
    elif estado_atual == 38:
        if caractere.isalpha() and (ord(caractere) >= 32 and ord(caractere) <= 126):
            lexema += caractere
            estado_atual = 1
            return 'TMF', lexema, estado_atual
        elif caractere.isdigit():
            lexema += caractere
            estado_atual = 2
            return 'TMF', lexema, estado_atual
        elif caractere == '&':
            lexema += caractere
            estado_atual = 37
        elif caractere == '|':
            lexema += caractere
            estado_atual = 24
            return 'TMF', lexema, estado_atual
        elif caractere == '<' or caractere == '>' or caractere == '=':
            lexema += caractere
            estado_atual = 3
            return 'TMF', lexema, estado_atual
        elif caractere == '!':
            lexema += caractere
            estado_atual = 19
            return 'TMF', lexema, estado_atual
        elif caractere in delimitadores:
            lexema += caractere
            estado_atual = 6
            return 'TMF', lexema, estado_atual
        elif caractere.isspace():
            lexema += caractere
            estado_atual = 0
            return 'TMF', lexema, estado_atual
        elif caractere == '/':
            lexema += caractere
            estado_atual = 8
            return 'TMF', lexema, estado_atual
        elif caractere == '+':
            lexema += caractere
            estado_atual = 14
            return 'TMF', lexema, estado_atual
        elif caractere == '-':
            lexema += caractere
            estado_atual = 16
            return 'TMF', lexema, estado_atual
        elif caractere == '*':
            lexema += caractere
            estado_atual = 18
            return 'TMF', lexema, estado_atual
        elif caractere == '"':
            lexema += caractere
            estado_atual = 10
            return 'TMF', lexema, estado_atual
        else:
            lexema += caractere
            estado_atual = 5
    return 0, lexema, estado_atual

    



pasta = './files'

#For para deletar os arquivos saídas ja existentes
for diretorio, pastas, arquivos in os.walk(pasta):
    for arquivo in arquivos:
        if "-saida" in arquivo:
            os.remove(diretorio + '\\' + arquivo)

#For para criação dos arquivos saídas
for diretorio, pastas, arquivos in os.walk(pasta):
    for arquivo in arquivos:
        acertos = []
        erros = []
        nome_arquivo = arquivo.split('.')[0]+"-saida.txt"

        #Leitura do conteúdo do arquivo de entrada
        with open(diretorio + '\\' + arquivo, 'r') as arquivo_entrada:
            texto = arquivo_entrada.readlines()
            
        #Lendo caractere por caractere para gerar o token
        lexema = ''
        estado_atual = 0
        numero_da_linha = 0
        for linha in texto:
            ultimo_token = 'STARTLINE'
            if estado_atual == 9:
                estado_atual = 0
                lexema = ''
            elif estado_atual == 12 or estado_atual == 10:
                erros.append(str(numero_da_linha) + ' CMF ' + lexema[:len(lexema)-1] + '\n')
                estado_atual = 0
                lexema = ''
            numero_da_linha += 1
            for caractere in linha.strip('\n')+' ':
                token, lexema, estado_atual = estados(estado_atual, caractere, lexema, ultimo_token)
                if estado_atual == 26 and lexema == '/*':
                    numero_da_linha_comentario_bloco = numero_da_linha
                if token != 0:
                    ultimo_token = token
                    if token == 'PRE' or token == 'IDE' or token == 'CAC' or token == 'NRO' or token == 'DEL' or token == 'REL' or token == 'LOG' or token == 'ART':
                        if estado_atual == 21 or estado_atual == 24:
                            acertos.append(str(numero_da_linha) + ' ' + token + ' ' + lexema[:len(lexema)-2] + '\n')
                            lexema = lexema[-2:]
                        else:
                            acertos.append(str(numero_da_linha) + ' ' + token + ' ' + lexema[:len(lexema)-1] + '\n')
                            lexema = lexema[-1]
                    else:
                        if estado_atual == 24 or estado_atual == 21:
                            erros.append(str(numero_da_linha) + ' ' + token + ' ' + lexema[:len(lexema)-2] + '\n')
                            lexema = lexema[-2:]
                        else:
                            erros.append(str(numero_da_linha) + ' ' + token + ' ' + lexema[:len(lexema)-1] + '\n')
                            lexema = lexema[-1]
                    if lexema.isspace():
                        lexema = ''
            if estado_atual == 26 or estado_atual == 27:
                lexema = lexema[:-1] + '\n'
        if estado_atual == 12 or estado_atual == 10:
            erros.append(str(numero_da_linha) + ' CMF ' + lexema[:len(lexema)-1] + '\n')
            estado_atual = 0
            lexema = ''
        elif estado_atual == 26 or estado_atual == 27:
            erros.append(str(numero_da_linha_comentario_bloco) + ' CoMF ' + lexema[:len(lexema)-1] + '\n')
            estado_atual = 0
            lexema = ''

        #Criando um objeto da classe analisadorSintatico e passando os tokens gerados no analisador léxico como atributo deste objeto.
        analisador_sintatico = analisadorSintatico(acertos)
        analisador_sintatico.startAnalisador()

        #Preenchendo o arquivo de saída com os resultados da análise sintática
        with open(diretorio + '\\' + nome_arquivo, "a") as arquivo_saida:
            if analisador_sintatico.erros_sintaticos:
                for i in analisador_sintatico.erros_sintaticos:
                    arquivo_saida.write(i+'\n')
            else:
                arquivo_saida.write("Seu codigo nao possui erros sintaticos.")