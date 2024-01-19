from AST import *
from Lexer import *

class Parser:
    def __init__(self, source:str):
        self.source = source
        self.lexer = Lexer(source)
        self.current_token = self.lexer.get_next_token()
        self.previous_token = None

    def parse(self) -> AST | None:
        return self._parse_statement()

    def _parse_expression(self):
        return self._parse_comparison()

    def _parse_comparison(self):
        left = self._parse_sum()
        while True:
            if(self._match(TokenType.EQUAL)):
                right = self._parse_sum()
                left = Equal(left, right)
            elif(self._match(TokenType.NOTEQUAL)):
                right = self._parse_sum()
                left = NotEqual(left, right)
            else: break
        return left

    def _parse_sum(self):
        left = self._parse_product()
        while True:
            if(self._match(TokenType.PLUS)):
                right = self._parse_product()
                left = Add(left, right)
            elif(self._match(TokenType.MINUS)):
                right = self._parse_product()
                left = Subtract(left, right)
            else: break
        return left

    def _parse_product(self):
        left = self._parse_unary()
        while True:
            if(self._match(TokenType.STAR)):
                right = self._parse_unary()
                left = Multiply(left, right)
            elif(self._match(TokenType.SLASH)):
                right = self._parse_unary()
                left = Divide(left, right)
            else: break
        return left

    def _parse_unary(self):
        if self._match(TokenType.NOT):
            operand = self._parse_atomic()
            return Not(operand)
        else:
            return self._parse_atomic()

    def _parse_atomic(self):
        if self._peek(TokenType.IDENTIFIER):
            return self._parse_call()
        elif self._match(TokenType.NUMBER):
            return Number(int(self.previous_token.value))
        elif self._match(TokenType.LPAREN):
            expression = self._parse_expression()
            self._consume(TokenType.RPAREN, "Expected ')' after expression.")
            return expression

    def _parse_call(self):
        if self._match(TokenType.IDENTIFIER):
            if self._peek(TokenType.LPAREN):
                function_name = str(self.previous_token.value)
                if self._match(TokenType.LPAREN):
                    args = self._parse_args()
                    self._consume(TokenType.RPAREN, "Expected ')' after expression.")
                    # if function_name == 'assert':
                    #     return Assert(args[0])
                    return Call(function_name, args)
            else:
                return Id(str(self.previous_token.value))

    def _parse_args(self):
        args = []
        if not self._peek(TokenType.RPAREN):
            args.append(self._parse_expression())
            while self._match(TokenType.COMMA):
                args.append(self._parse_expression())
        return args

    def _parse_statement(self):
        if self._peek(TokenType.RETURN):
            return self._parse_return_statement()
        elif self._peek(TokenType.IF):
            return self._parse_if_statement()
        elif self._peek(TokenType.WHILE):
            return self._parse_while_statement()
        elif self._peek(TokenType.VAR):
            return self._parse_var_statement()
        elif self._peek(TokenType.IDENTIFIER) and self._peeknext(TokenType.ASSIGN):
            return self._parse_assignment_statement()
        elif self._peek(TokenType.LBRACE):
            return self._parse_block_statement()
        elif self._peek(TokenType.FUNCTION):
            return self._parse_function_statement()
        elif self._peek(TokenType.IDENTIFIER):
            return self._parse_expression_statement()
        
    def _parse_function_statement(self):
        if self._match(TokenType.FUNCTION):
            self._consume(TokenType.IDENTIFIER, "Expected function name")
            function_name = str(self.previous_token.value)
            self._consume(TokenType.LPAREN, "Expected parameters")
            paramenters = self._parse_parameters()
            self._consume(TokenType.RPAREN, "Expected Right PAREN")
            body = self._parse_block_statement()
            # if function_name == 'main':
            #     return Main(body.statements)
            return Function(function_name, paramenters, body)

    def _parse_parameters(self):
        paramenters = []
        if not self._peek(TokenType.RPAREN):
            self._consume(TokenType.IDENTIFIER, "Expectede parameters")
            paramenters.append(self.previous_token.value)
            while self._match(TokenType.COMMA):
                self._consume(TokenType.IDENTIFIER, "Expected parameters")          
                paramenters.append(self.previous_token.value)
        return paramenters

    def _parse_block_statement(self):
        self._consume(TokenType.LBRACE, "Expected {")
        statements = []
        while not self._peek(TokenType.RBRACE):
            statements.append(self._parse_statement())
        self._consume(TokenType.RBRACE, "Expected }")
        return Block(statements)

    def _parse_assignment_statement(self):
        if self._match(TokenType.IDENTIFIER):
            name = str(self.previous_token.value)
            if self._match(TokenType.ASSIGN):
                value = self._parse_expression()
                self._consume(TokenType.SEMICOLON, "Expected ;")
                return Assign(name, value)

    def _parse_var_statement(self):
        self._consume(TokenType.VAR, "Expected")
        self._consume(TokenType.IDENTIFIER, "Expected")
        var_name = str(self.previous_token.value)
        self._consume(TokenType.ASSIGN, "Expected")
        value = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "Expected")
        return Var(var_name, value)

    def _parse_while_statement(self):
        self._consume(TokenType.WHILE, "Expected")
        self._consume(TokenType.LPAREN, "Expected")
        conditional = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected")
        body = self._parse_block_statement()
        return While(conditional, body)

    def _parse_if_statement(self):
        self._consume(TokenType.IF, "Expected")
        self._consume(TokenType.LPAREN, "Expected")
        conditional = self._parse_expression()
        self._consume(TokenType.RPAREN, "Expected")
        consequence = self._parse_statement()
        if self._match(TokenType.ELSE):
            alternative = self._parse_statement()
            return If(conditional, consequence, alternative)
        return If(conditional, consequence, Block([]))

    def _parse_expression_statement(self):
        expression = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "exptec")
        return expression

    def _parse_return_statement(self):
        self._consume(TokenType.RETURN, "expected")
        expression = self._parse_expression()
        self._consume(TokenType.SEMICOLON, "expected")
        return Return(expression)
    
    def _match(self, token_type:TokenType) -> bool:
        if self._peek(token_type):
            self.previous_token = self.current_token
            self.current_token = self.lexer.get_next_token()
            return True
        return False

    def _peek(self, token_type:TokenType) -> bool:
        if(self.current_token == token_type):
            return True
        return False

    def _peeknext(self, token_type:TokenType) -> bool:
        return self.lexer.peek_next_token() == token_type

    def _consume(self, token_type:TokenType, message:str):
        if self._peek(token_type):
            self.previous_token = self.current_token
            self.current_token = self.lexer.get_next_token()
        else:
            raise Exception(self.lexer.get_current_line_in_source())