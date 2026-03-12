Учебный компилятор для упрощенного C-подобного языка.

##  Требования


- Python 3.13
- Git

## Cтарт

### 1. Клонирование репозитория
```bash
git clone https://github.com/Fanatik-Karasik/Compilator_pulyator.git
cd Compilator_pulyator

```


# MiniCompiler (Compilator_pulyator)

## Sprint 2: Parser & AST

## Requirements
- Python 3.7+

## Quick Start

### Run Lexer
```powershell
python src/main.py examples/hello.src --mode lex

Run Parser (AST output)
python src/main.py examples/hello.src --mode parse --ast-format text

Generate DOT file for Graphviz
python src/main.py examples/hello.src --mode parse --ast-format dot -o ast.dot
dot -Tpng ast.dot -o ast.png

Run All Tests
python tests/test_runner.py
```
