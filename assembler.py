import re

class Y86Assembler:
    def __init__(self):
        self.instructions = {
            'halt': '00', 'nop': '10', 'rrmovq': '20', 'irmovq': '30',
            'rmmovq': '40', 'mrmovq': '50', 'addq': '60', 'subq': '61',
            'andq': '62', 'xorq': '63', 'jmp': '70', 'jle': '71',
            'jl': '72', 'je': '73', 'jne': '74', 'jge': '75', 'jg': '76',
            'call': '80', 'ret': '90', 'pushq': 'A0', 'popq': 'B0'
        }
        self.registers = {
            '%rax': '0', '%rcx': '1', '%rdx': '2', '%rbx': '3',
            '%rsp': '4', '%rbp': '5', '%rsi': '6', '%rdi': '7'
        }
        self.labels = {}
        self.memory = {}
        self.address = 0

    def parse_directive(self, line):
        if line.startswith('.pos'):
            self.address = int(line.split()[1], 16)
        elif line.startswith('.align'):
            align = int(line.split()[1])
            self.address = (self.address + align - 1) // align * align
        elif line.startswith('.long') or line.startswith('.quad'):
            value = int(line.split()[1], 0)
            self.memory[self.address] = f'{value:016x}'
            self.address += 8
        elif line.startswith('.byte'):
            value = int(line.split()[1], 0)
            self.memory[self.address] = f'{value:02x}'
            self.address += 1
        elif line.startswith('.word'):
            value = int(line.split()[1], 0)
            self.memory[self.address] = f'{value:04x}'
            self.address += 2

    def assemble(self, lines):
        for line in lines:
            line = line.strip()
            if ':' in line:
                label, rest = line.split(':', 1)
                self.labels[label.strip()] = self.address
                line = rest.strip()
            if line.startswith('.'):
                self.parse_directive(line)
            elif line:
                self.address += 1  
        
        self.address = 0
        output = []
        for line in lines:
            line = line.strip()
            if ':' in line:
                _, line = line.split(':', 1)
            line = line.strip()
            if line.startswith('.'):
                self.parse_directive(line)
            elif line:
                parts = line.split()
                opcode = self.instructions.get(parts[0])
                if opcode:
                    operands = ''
                    if len(parts) > 1:
                        operands_list = parts[1].replace(',', '').split()
                        for op in operands_list:
                            if op in self.registers:
                                operands += self.registers[op]
                            elif op in self.labels:
                                operands += f'{self.labels[op]:04x}'
                            else:
                                operands += f'{int(op.strip("$"), 0):02x}'
                    output.append(f'{self.address:04x}: {opcode} {operands}')
                    self.address += 1
        
        return '\n'.join(output)

# Ex
code = [
    '.pos 0x100',
    'start: irmovq $10, %rax',
    'addq %rbx, %rax',
    'jmp start',
    '.quad 0x12345678',
    '.byte 0xff',
    '.word 0x1234',
    'pushq %rbp',
    'call start'
]

assembler = Y86Assembler()
result = assembler.assemble(code)
print(result)
