def get_label_index():
    try:
        get_label_index.counter += 1
    except AttributeError:
        get_label_index.counter = 1
    return f'.L{get_label_index.counter}'

class Environment:
    def __init__(self, locals:dict[str, int] = dict(), next_local_offset:int = 0):
        self.locals = locals.copy()
        self.next_local_offset = next_local_offset

class AST:
    def __eq__(self, other) -> bool:
        return type(self) is type(other) and self.__dict__ == other.__dict__
    
    def emit(self, content):
        with open('./out.s', 'a') as file:
            file.write(content)
            file.write('\n')

# class Main(AST):
#     def __init__(self, statements:list[AST]):
#         self.statements = statements

#     def __repr__(self):
#         return f'{self.__class__.__name__}({[stmt for stmt in self.statements]})'

#     def emit(self, env:Environment):
#         super().emit('.global main')
#         super().emit('main:')
#         super().emit('push {fp, lr}')
#         for statement in self.statements:
#             statement.emit(env)
#         super().emit('mov r0, #0')
#         super().emit('pop {fp, pc}')
    
# class Assert(AST):
#     def __init__(self, condition:AST):
#         self.condition = condition

#     def __repr__(self):
#         return f'{self.__class__.__name__}({self.condition})'

#     def emit(self, env:Environment):
#         self.condition.emit(env)
#         super().emit('cmp r0, #1')
#         super().emit("moveq r0, #'T'")
#         super().emit("movne r0, #'F'")
#         super().emit('bl putchar')

class Number(AST):
    def __init__(self, value:int):
        self.value = value

    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'

    def emit(self, env:Environment):
        super().emit(f'ldr r0, ={self.value}')

class Id(AST):
    def __init__(self, value:str):
        self.value = value

    def emit(self, env:Environment):
        try:
            offset = env.locals[self.value]
            super().emit(f'ldr r0, [fp, #{offset}]')
        except KeyError:
            raise Exception(f'Undefined variable: {self.value}')
        
    def __repr__(self):
        return f'{self.__class__.__name__}({self.value})'    

class Not(AST):
    def __init__(self, term:AST):
        self.term = term

    def emit(self, env:Environment):
        self.term.emit(env)
        super().emit('cmp r0, #0')
        super().emit('moveq r0, #1')
        super().emit('movne r0, #0')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.term})'

class Equal(AST):
    def __init__(self, left:AST, right:AST):
        self.left = left
        self.right = right

    def emit(self, env:Environment):
        self.left.emit(env)
        super().emit('push {r0, ip}')
        self.right.emit(env)
        super().emit('pop {r1, ip}')
        super().emit('cmp r0, r1')
        super().emit('moveq r0, #1')
        super().emit('movne r0, #0')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.left},{self.right})'

class NotEqual(AST):
    def __init__(self, left:AST, right:AST):
        self.left = left
        self.right = right

    def emit(self, env:Environment):
        self.left.emit(env)
        super().emit('push {r0, ip}')
        self.right.emit(env)
        super().emit('pop {r1, ip}')
        super().emit('cmp r0, r1')
        super().emit('moveq r0, #0')
        super().emit('movne r0, #1')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.left},{self.right})'

class Add(AST):
    def __init__(self, left:AST, right:AST):
        self.left = left
        self.right = right

    def emit(self, env:Environment):
        self.right.emit(env)
        super().emit('push {r0, ip}')
        self.left.emit(env)
        super().emit('pop {r1, ip}')
        super().emit('add r0, r0, r1')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.left},{self.right})'

class Subtract(AST):
    def __init__(self, left:AST, right:AST):
        self.left = left
        self.right = right

    def emit(self, env:Environment):
        self.right.emit(env)
        super().emit('push {r0, ip}')
        self.left.emit(env)
        super().emit('pop {r1, ip}')
        super().emit('sub r0, r0, r1')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.left},{self.right})'

class Multiply(AST):
    def __init__(self, left:AST, right:AST):
        self.left = left
        self.right = right

    def emit(self, env:Environment):
        self.right.emit(env)
        super().emit('push {r0, ip}')
        self.left.emit(env)
        super().emit('pop {r1, ip}')
        super().emit('mul r0, r0, r1') 

    def __repr__(self):
        return f'{self.__class__.__name__}({self.left},{self.right})'

class Divide(AST):
    def __init__(self, left:AST, right:AST):
        self.left = left
        self.right = right

    def emit(self, env:Environment):
        self.right.emit(env)
        super().emit('push {r0, ip}')
        self.left.emit(env)
        super().emit('pop {r1, ip}')
        super().emit('udiv r0, r0, r1') 

    def __repr__(self):
        return f'{self.__class__.__name__}({self.left},{self.right})'

class Call(AST):
    def __init__(self, callee:str, arguments:list[AST]):
        self.callee = callee
        self.arguments = arguments

    def emit(self, env:Environment):
        count = len(self.arguments)
        if count == 0:
            super().emit(f'bl {self.callee}')
        elif count == 1:
            self.arguments[0].emit(env)
            super().emit(f'bl {self.callee}')
        elif count >= 2 and count <= 4:
            super().emit('sub sp, sp, #16')
            for i, arg in enumerate(self.arguments):
                arg.emit(env)
                super().emit(f'str r0, [sp, #{4 * i}]')
            super().emit('pop {r0, r1, r2, r3}')
            super().emit(f'bl {self.callee}')
        else:
            raise Exception('More than 4 arguments not supported')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.callee},{[arg for arg in self.arguments]})'

class Return(AST):
    def __init__(self, term:AST):
        self.term = term

    def emit(self, env:Environment):
        self.term.emit(env)
        super().emit('mov sp, fp')
        super().emit('pop {fp, pc}')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.term})'

class Block(AST):
    def __init__(self, statements:list[AST]):
        self.statements = statements

    def emit(self, env:Environment):
        for stmt in self.statements:
            stmt.emit(env)

    def __repr__(self):
        return f'{self.__class__.__name__}({[stmt for stmt in self.statements]})'

class If(AST):
    def __init__(self, conditional:AST, consequence:AST, alternative:AST):
        self.conditional = conditional
        self.consequence = consequence
        self.alternative = alternative

    def emit(self, env:Environment):
        if_false_label = get_label_index()
        end_if_label = get_label_index()
        self.conditional.emit(env)
        super().emit('cmp r0, #0')
        super().emit(f'beq {if_false_label}')
        self.consequence.emit(env)
        super().emit(f'b {end_if_label}')
        super().emit(f'{if_false_label}:')
        self.alternative.emit(env)
        super().emit(f'{end_if_label}:')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.conditional},{self.consequence},{self.alternative})'
        
class Function(AST):
    def __init__(self, name:str, paramenters:list[AST], body:AST):
        self.name = name
        self.paramenters = paramenters
        self.body = body

    def emit_prologue(self):
        super().emit('push {fp, lr}')
        super().emit('mov fp, sp')
        super().emit('push {r0, r1, r2, r3}')

    def emit_epilogue(self):
        super().emit('mov sp, fp')
        super().emit('mov r0, #0')
        super().emit('pop {fp, pc}')

    def set_environment(self):
        locals = dict()
        for i, parameter in enumerate(self.paramenters):
            locals[parameter] = 4 * i - 16
        next_local_offset = -20
        return Environment(locals, next_local_offset)

    def emit(self, env:Environment):
        if len(self.paramenters) > 4:
            raise Exception('More than 4 parameters not supported')
        super().emit('')
        super().emit(f'.global {self.name}')
        super().emit(f'{self.name}:')
        self.emit_prologue()
        env = self.set_environment()
        self.body.emit(env)
        self.emit_epilogue()

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name},{[param for param in self.paramenters]},{self.body})'

class Var(AST):
    def __init__(self, name:str, value:AST):
        self.name = name
        self.value = value
    
    def emit(self, env:Environment):
        self.value.emit(env)
        super().emit('push {r0, ip}')
        env.locals[self.name] = env.next_local_offset - 4
        env.next_local_offset -= 8

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name},{self.value})'

class Assign(AST):
    def __init__(self, name:str, value:AST):
        self.name = name
        self.value = value

    def emit(self, env:Environment):
        self.value.emit(env)
        try:
            offset = env.locals[self.name]
            super().emit(f'str r0, [fp, #{offset}]')
        except KeyError:
            raise Exception(f'Undefined variable: {self.name}')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.name},{self.value})'

class While(AST):
    def __init__(self, conditional:AST, body:AST):
        self.conditional = conditional
        self.body = body

    def emit(self, env:Environment):
        loop_start = get_label_index()
        loop_end = get_label_index()

        super().emit(f'{loop_start}:')
        self.conditional.emit(env)
        super().emit('cmp r0, #0')
        super().emit(f'beq {loop_end}')
        self.body.emit(env)
        super().emit(f'b {loop_start}')
        super().emit(f'{loop_end}:')

    def __repr__(self):
        return f'{self.__class__.__name__}({self.conditional},{self.body})'

if __name__ == '__main__':
    main = Main([])
    main.emit()