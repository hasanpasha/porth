#!/usr/bin/env python3

import sys
import subprocess

class Unrachable(Exception):
    def __init__(self, msg=""):
        super().__init__(f"unreachable: {msg}")

class ExhaustiveHandling(Exception):
    def __init__(self, msg=""):
        super().__init__(f"exhaustive handling: {msg}")

iota_counter = 0
def iota(reset=False):
    global iota_counter
    if reset:
        iota_counter = 0
    result = iota_counter
    iota_counter += 1
    return result

OP_PUSH = iota()
OP_PLUS = iota()
OP_MINUS = iota()
OP_DUMP = iota()
OP_EQUAL = iota()
COUNT_OPS = iota()

def push(x):
    return (OP_PUSH, x)

def plus():
    return (OP_PLUS, )

def minus():
    return (OP_MINUS, )

def dump():
    return (OP_DUMP, )

def equal():
    return (OP_EQUAL, )

def call_cmd(cmd) -> bool:
    print("[CMD] ", " ".join(cmd))
    if subprocess.run(cmd).returncode == 0:
        return True
    else:
        return False

def file_write_lines(file_name, lines: list, *append_files) -> bool:
    print(f"[PROC] writing to file {file_name}")
    with open(file_name, "w") as output:
        if len(append_files) > 0:
            for fn in append_files:
                with open(fn, 'r') as f:
                    output.write(f.read() + '\n')
        for line in lines:
            if output.write(line + '\n') != (len(line)+1):
                return False

    return True
       
def lines_from_file(file_name) -> list:
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            lines[i] = lines[i].replace('\n', '')
        return lines


def simulate_program(program):
    stack = []
    for op in program:
        if COUNT_OPS != 5: 
            raise ExhaustiveHandling()

        if op[0] == OP_PUSH:
            stack.append(op[1])
        elif op[0] == OP_PLUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(a + b)
        elif op[0] == OP_MINUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(b - a)
        elif op[0] == OP_DUMP:
            a = stack.pop()
            print(a)
        elif op[0] == OP_EQUAL:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(a == b))
        else:
            raise Unreachable()

def compile_program(program, output_file_name):
    dump_function_file_name = "dump.asm"
    dump_function_lines = lines_from_file(dump_function_file_name)
    asm_program = []
    asm_program.append("segment .text")
    asm_program.append("global _start")
    asm_program.extend(dump_function_lines)
    asm_program.append("_start:")
    for op in program:
        if COUNT_OPS != 5: 
            raise ExhaustiveHandling()
        
        if op[0] == OP_PUSH:
            asm_program.append(f"\t;; -- push {op[1]} --")
            asm_program.append(f"\tpush {op[1]}")
        elif op[0] == OP_PLUS:
            asm_program.append("\t;; -- plus --")
            asm_program.append("\tpop rax")
            asm_program.append("\tpop rbx")
            asm_program.append("\tadd rax, rbx")
            asm_program.append("\tpush rax")
        elif op[0] == OP_MINUS:
            asm_program.append("\t;; -- minux --")
            asm_program.append("\tpop rax")
            asm_program.append("\tpop rbx")
            asm_program.append("\tsub rbx, rax")
            asm_program.append("\tpush rbx")
        elif op[0] == OP_DUMP:
            asm_program.append("\t;; -- dump --")
            asm_program.append("\tpop rdi")
            asm_program.append("\tcall dump")
        elif op[0] == OP_EQUAL:
            asm_program.append("\t;; -- equal --")
            asm_program.append("\tmov rcx, 0")
            asm_program.append("\tmov rdx, 1")
            asm_program.append("\tpop rax")
            asm_program.append("\tpop rbx")
            asm_program.append("\tcmp rax, rbx")
            asm_program.append("\tcmove rcx, rdx")
            asm_program.append("\tpush rcx")
        else:
            raise Unreachable()
    asm_program.append("\tmov rax, 0x3c")
    asm_program.append("\tmov rdi, 0x0")
    asm_program.append("\tsyscall")

    if asm_program:
        return file_write_lines(output_file_name, asm_program,)
    return False

def parse_word_as_op(token):
    (file_path, row, col, word) = token

    if (COUNT_OPS != 5):
        raise ExhaustiveHandling("in parse_word_as_op")

    if word == "+":
        return plus()
    elif word == "-":
        return minus()
    elif word == ".":
        return dump()
    elif word == "=":
        return equal()
    else:
        try:
            return push(int(word))
        except ValueError as err:
            print(f"{file_path}:{row}:{col}: {err}")
            exit(1)

def find_col(line, start, predicate):
    while start < len(line) and not predicate(line[start]):
        start += 1
    return start

def lex_line(line):
    col = find_col(line, 0, lambda x: not x.isspace())
    while col < len(line):
        col_end = find_col(line, col, lambda x: x.isspace())
        yield (col, line[col:col_end])
        col = find_col(line, col_end, lambda x: not x.isspace())

def lex_file(file_path) -> list:
    with open(file_path, 'r') as f:
        return [(file_path, row, col, token)
                for (row, line) in enumerate(f.readlines())
                for (col, token) in lex_line(line)]

def load_program_from_file(file_path) -> bool:
    return [parse_word_as_op(token) for token in lex_file(file_path)]

def get_args():
    from argparse import ArgumentParser

    parser = ArgumentParser(description="Porth language compiler.")
    subparser = parser.add_subparsers(help="select mode", dest="subcommand")
    sim_parse = subparser.add_parser("sim", help="Simulate the program.")
    com_parse = subparser.add_parser("com", help="Compile the program.")
    parser.add_argument("file_path", metavar="file_path", type=str,
                        help="The input file path")
    return parser.parse_args()

def get_program_name(program_path):
    return "".join(program_path.split('/')[-1].split('.')[0:-1])

if __name__ == '__main__':
    command_arguments = get_args()
    program_path = command_arguments.file_path
    subcommand = command_arguments.subcommand
    program_name = get_program_name(program_path)
    
    if subcommand == "sim":
        program = load_program_from_file(program_path)
        if not program:
            exit(-1)
        simulate_program(program)

    elif subcommand == "com":
        program = load_program_from_file(program_path)
        if not program:
            exit(-1)
        if not (compile_program(program, f"{program_name}.asm", )):
            exit(1)
        if not call_cmd(["nasm", "-felf64", f"{program_name}.asm",]):
            exit(2)
        if not call_cmd(["ld", "-o", program_name, f"{program_name}.o", ]):
            exit(3)
