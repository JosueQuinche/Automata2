import re
from enum import Enum

# Definición de los tipos de tokens que el analizador reconocerá
class TokenType(Enum):
    PALABRA_RESERVADA = 1     # palabras reservadas del lenguaje (if, else, etc.)
    IDENTIFICADOR = 2         # nombres de variables, funciones, clases
    ENTERO = 3                # números enteros
    FLOTANTE = 4              # números con punto decimal
    OPERADOR = 5              # operadores simples (+, -, etc.)
    DELIMITADOR = 6           # símbolos que delimitan bloques o instrucciones (;, {}, etc.)
    CADENA = 7                # cadenas de texto entre comillas dobles
    COMENTARIO = 8            # comentarios de línea o bloque
    OPERADOR_COMPUESTO = 9    # operadores formados por dos símbolos (==, !=, &&, etc.)
    HEXADECIMAL = 10          # números hexadecimales (0x...)
    BOOLEANO = 11             # valores booleanos true o false
    EOF = 12                  # fin del archivo

# Clase principal del analizador léxico
class AnalizadorLexico:
    def __init__(self):
        # Conjunto de palabras reservadas reconocidas por el lenguaje
        self.palabras_reservadas = {'if', 'else', 'while', 'for', 'int', 'float', 'return', 'void', 'function', 'class', 'true', 'false'}
        # Operadores simples permitidos
        self.operadores = {'+', '-', '*', '/', '=', '<', '>', '!', '&', '|', '%', '^'}
        # Operadores compuestos permitidos (de dos caracteres)
        self.operadores_compuestos = {'==', '!=', '<=', '>=', '&&', '||', '+=', '-=', '*=', '/='}
        # Delimitadores usados en la sintaxis
        self.delimitadores = {'(', ')', '{', '}', '[', ']', ';', ',', ':', '.'}
        # Estado inicial del autómata de análisis
        self.estado_actual = 'inicio'
        # Variable para construir lexemas (tokens)
        self.lexema = ''
        # Contador de línea actual, empieza en 1
        self.linea = 1
        # Lista donde se almacenarán los tokens reconocidos
        self.tokens = []
        # Lista donde se almacenarán los errores detectados
        self.errores = []

    # Método principal que realiza el análisis léxico
    def analizar(self, ruta_archivo):
        # Reiniciar las variables para un nuevo análisis
        self.estado_actual = 'inicio'   # Estado inicial
        self.lexema = ''                # Lexema vacío
        self.linea = 1                 # Contador de líneas inicia en 1
        self.tokens = []               # Lista vacía para tokens
        self.errores = []              # Lista vacía para errores

        # Intentar abrir y leer el archivo
        try:
            # Abrir el archivo en modo lectura usando la ruta proporcionada
            # 'with' asegura que el archivo se cierre automáticamente después
            with open(ruta_archivo, 'r') as archivo:
                # Leer todo el contenido y guardarlo en la variable 'contenido' como string
                contenido = archivo.read()
        except FileNotFoundError:
            # Si el archivo no se encuentra, mostrar mensaje de error y detener análisis
            print("\n Error: Archivo no encontrado.")
            return False

        # Agregar un espacio al final para facilitar el análisis y evitar perder el último token
        contenido += ' '

        i = 0  # Índice para recorrer carácter por carácter el contenido

        # Bucle principal para procesar todo el texto leído
        while i < len(contenido):
            c = contenido[i]  # Caracter actual

            # Estado inicial del autómata: buscar qué tipo de token comenzar
            if self.estado_actual == 'inicio':
                # Ignorar espacios y saltos de línea, actualizando contador de líneas
                if c.isspace(): # isspace verifica espacios, tabulaciones y saltos de línea
                    if c == '\n': # Si el carácter es salto de línea
                        self.linea += 1 # Incrementar el contador de línea para seguimiento de posición
                    i += 1 # Avanzar al siguiente carácter
                    continue # Saltar al siguiente ciclo del while sin procesar más nada en esta iteración

                # Detectar inicio de comentario (línea o bloque)
                if c == '/':
                    if i+1 < len(contenido) and contenido[i+1] == '/':
                        self.estado_actual = 'comentario_linea'  # Comentario hasta fin de línea
                        i += 1
                    elif i+1 < len(contenido) and contenido[i+1] == '*':
                        self.estado_actual = 'comentario_bloque'  # Comentario multilínea
                        i += 1
                    else:
                        self.lexema = c
                        self.estado_actual = 'operador'
                # Detectar inicio de cadena de texto
                elif c == '"':
                    self.estado_actual = 'cadena'
                    i += 1
                    continue
                # Detectar identificadores o palabras reservadas (letras o '_')
                elif c.isalpha() or c == '_':
                    self.estado_actual = 'identificador'
                    self.lexema += c
                # Detectar números enteros (dígitos)
                elif c.isdigit():
                    self.estado_actual = 'entero'
                    self.lexema += c
                # Detectar operadores simples
                elif c in self.operadores:
                    self.lexema += c
                    self.estado_actual = 'operador'
                # Detectar delimitadores
                elif c in self.delimitadores:
                    self.agregar_token(TokenType.DELIMITADOR, c, 'q0')
                else:
                    # Carácter no reconocido: registrar error
                    self.errores.append(f"Línea {self.linea}: Carácter no reconocido '{c}'")
                i += 1

            # Estado para reconocer identificadores y palabras reservadas
            elif self.estado_actual == 'identificador':
                # Mientras sean letras, dígitos o guiones bajos, seguir formando el lexema
                if c.isalnum() or c == '_':
                    self.lexema += c
                    i += 1
                else:
                    # Al terminar, revisar si es palabra reservada, booleano o identificador normal
                    if self.lexema in self.palabras_reservadas:
                        token_type = TokenType.PALABRA_RESERVADA # Si el lexema está en la lista de palabras reservadas, 
                        #marcarlo como tal
                        estado = 'q1' # Estado asociado para tokens de palabra reservada
                    elif self.lexema in ['true', 'false']:
                        token_type = TokenType.BOOLEANO
                        estado = 'q10'
                    else:
                        token_type = TokenType.IDENTIFICADOR
                        estado = 'q2'
                    # Agregar token a la lista
                    self.agregar_token(token_type, self.lexema, estado)
                    # Reiniciar lexema y volver al estado inicial
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            # Estado para reconocer números enteros
            elif self.estado_actual == 'entero':
                # Si sigue siendo dígito, agregar al lexema
                if c.isdigit():
                    self.lexema += c
                    i += 1
                # Si aparece un punto, cambiar a estado flotante
                elif c == '.':
                    self.lexema += c
                    self.estado_actual = 'flotante'
                    i += 1
                # Detectar números hexadecimales (empiezan con 0x)
                elif c.lower() == 'x' and len(self.lexema) == 1 and self.lexema[0] == '0':#lower convierte a minúsculas
                    self.lexema += c
                    self.estado_actual = 'hexadecimal'
                    i += 1
                else:
                    # Termina número entero, agregar token
                    self.agregar_token(TokenType.ENTERO, self.lexema, 'q3')
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            # Estado para reconocer números flotantes
            elif self.estado_actual == 'flotante':
                # Seguir agregando dígitos después del punto
                if c.isdigit():# isdigit verifica si el carácter es un dígito
                    self.lexema += c
                    i += 1
                else:
                    # Finaliza número flotante, agregar token
                    self.agregar_token(TokenType.FLOTANTE, self.lexema, 'q4')
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            # Estado para reconocer números hexadecimales
            elif self.estado_actual == 'hexadecimal':
                # Mientras sean dígitos o letras a-f/A-F, seguir agregando, 
                # es decir que el lexema va creciendo con cada carácter 
                # válido (dígito o letra hexadecimal) 
                if c.isdigit() or c.lower() in 'abcdef':
                    self.lexema += c
                    i += 1
                else:
                    # Termina número hexadecimal, agregar token
                    self.agregar_token(TokenType.HEXADECIMAL, self.lexema, 'q9')
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            # Estado para reconocer operadores simples o compuestos
            elif self.estado_actual == 'operador':
                # Si el siguiente carácter también es operador, formar operador compuesto
                if c in self.operadores:
                    self.lexema += c
                    i += 1
                else:
                    # Revisar si lexema es operador compuesto o simple
                    if self.lexema in self.operadores_compuestos:
                        self.agregar_token(TokenType.OPERADOR_COMPUESTO, self.lexema, 'q8')
                    else:
                        self.agregar_token(TokenType.OPERADOR, self.lexema, 'q5')
                    # Reiniciar lexema y estado
                    self.lexema = ''
                    self.estado_actual = 'inicio'

            # Estado para reconocer cadenas de texto entre comillas dobles
            elif self.estado_actual == 'cadena':
                if c == '"':
                    # Se cerró la cadena, agregar token
                    self.agregar_token(TokenType.CADENA, self.lexema, 'q6')
                    self.lexema = ''
                    self.estado_actual = 'inicio'
                    i += 1
                elif c == '\n':
                    # Si llega a un salto de línea sin cerrar, error por cadena no cerrada
                    self.errores.append(f"Línea {self.linea}: Cadena no cerrada")#append agrega un elemento al final de la lista
                    self.lexema = ''
                    self.estado_actual = 'inicio'
                else:
                    # Agregar caracteres a la cadena
                    self.lexema += c
                    i += 1

            # Estado para comentarios de línea (// hasta fin de línea)
            elif self.estado_actual == 'comentario_linea':
                if c == '\n':
                    # Al llegar al fin de línea, agregar token comentario y volver al inicio
                    self.agregar_token(TokenType.COMENTARIO, self.lexema, 'q7')
                    self.lexema = ''
                    self.estado_actual = 'inicio'
                    self.linea += 1
                else:
                    # Seguir acumulando caracteres del comentario
                    self.lexema += c
                    i += 1

            # Estado para comentarios de bloque (/* ... */)
            elif self.estado_actual == 'comentario_bloque':
                # Detectar cierre de comentario de bloque */
                if c == '*' and i+1 < len(contenido) and contenido[i+1] == '/':
                    self.agregar_token(TokenType.COMENTARIO, self.lexema, 'q7')
                    self.lexema = ''
                    self.estado_actual = 'inicio'
                    i += 2  # saltar el */
                elif c == '\n':
                    # Contar líneas en comentario multilínea
                    self.linea += 1
                    i += 1
                else:
                    # Seguir acumulando comentario
                    self.lexema += c
                    i += 1

        # Al finalizar todo el texto, agregar token EOF para indicar fin del archivo
        self.agregar_token(TokenType.EOF, 'EOF', 'q12')
        return True

    # Método para agregar un token reconocido a la lista y mostrar en consola
    def agregar_token(self, tipo, lexema, estado):# tipo es el tipo de token, lexema es el texto del token 
        #y estado es el estado del autómata.
        # Agregar el token a la lista de tokens encontrados
        self.tokens.append((tipo, lexema, self.linea, estado))# es una lista de tuplas que contiene el tipo 
        #de token, el lexema, la línea y el estado del autómata.
        # Reiniciar lexema para el siguiente token
        # Imprimir en consola el token reconocido
        print(f"✔ Token reconocido: {tipo.name:<20} | Lexema: '{lexema}' | Línea: {self.linea}")

    # Método para imprimir en consola todos los tokens encontrados y errores
    #self es una instancia actual de la clase AnalizadorLexico.
    def imprimir_resultados(self):
        print("\n════════════════ TOKENS ENCONTRADOS ════════════════")
        print("{:<20} {:<30} {:<10} {:<10}".format('TIPO', 'LEXEMA', 'LÍNEA', 'ESTADO'))
        print("-" * 70)# Línea de separación para mejor legibilidad
        # Recorrer la lista de tokens y mostrarlos en formato tabular
        for token in self.tokens:
            print("{:<20} {:<30} {:<10} {:<10}".format(
                token[0].name,
                repr(token[1])[1:-1],  # Mostrar lexema sin comillas extras
                token[2],
                token[3]
            ))

        # Mostrar errores encontrados, si hay alguno
        if self.errores:
            print("\n══════════════════ ERRORES ══════════════════")
            for error in self.errores:
                print(error)
        else:
            print("\n Análisis léxico completado sin errores.")

# Bloque principal para ejecutar el analizador desde consola
# __name__ es una variable especial que indica si el script se está ejecutando directamente
# o si se está importando como módulo en otro script.
if __name__ == "__main__":# Este bloque se ejecuta solo si el script se corre directamente
    analizador = AnalizadorLexico()  # Crear instancia del analizador
    nombre_archivo = input("\nIngrese la ruta del archivo .txt a analizar: ")  # Solicitar ruta del archivo

    # Iniciar análisis, si se pudo leer el archivo
    if analizador.analizar(nombre_archivo):
        analizador.imprimir_resultados()  # Mostrar tokens y errores (si hay)

    input("\nPresione cualquier tecla para salir...")  # Esperar tecla para salir
