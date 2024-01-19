from Parser import *
from AST import *
from Lexer import *
import sys

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python main.py <file_path>')
    else:
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r') as file:
                file_content = file.read()

                with open('./out.s', 'w') as file:
                    pass
                
                parser = Parser(f'{{{file_content}}}')
                parsed = parser.parse()
                parsed.emit(Environment())
                
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"An error occurred: {e}")

        