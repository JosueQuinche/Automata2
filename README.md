# Analizador Léxico en Python

Este proyecto es un **analizador léxico básico** implementado en Python que lee un archivo de código fuente y extrae los tokens presentes, tales como palabras reservadas, identificadores, números, operadores y delimitadores.

---

## Características principales

- Reconoce múltiples tipos de tokens:
  - Palabras reservadas (`if`, `else`, `while`, `int`, etc.)
  - Identificadores (variables, funciones)
  - Literales numéricos (enteros, flotantes, hexadecimales)
  - Cadenas entre comillas dobles
  - Operadores simples y compuestos (`+`, `==`, `+=`, etc.)
  - Delimitadores (paréntesis, llaves, punto y coma, etc.)
  - Comentarios de línea y bloque

- Detecta errores léxicos como:
  - Cadenas no cerradas
  - Caracteres no válidos

- Genera una lista detallada de tokens con información de tipo, lexema, línea y estado.

---

## Uso

1. Escribe o coloca el código fuente a analizar en un archivo `.txt` (por ejemplo, `entrada.txt`).

2. Ejecuta el analizador desde la terminal:

```bash
python analizador_lexico.py
