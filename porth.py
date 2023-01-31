#!/usr/bin/env python3

import sys
import subprocess

class Unrachable(Exception):
    def __init__(self, msg=""):
        super().__init__("unreachable", msg)

class ExhaustiveHandling(Exception):
    def __init__(self, msg=""):
        super().__init__("exhaustive handling", msg)

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
COUNT_OPS = iota()

def push(x):
    return (OP_PUSH, x)

def plus():
    return (OP_PLUS, )

def minus():
    return (OP_MINUS, )

def dump():
    return (OP_DUMP, )

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
        if COUNT_OPS != 4: 
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
        if COUNT_OPS != 4: 
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
        else:
            raise Unreachable()
    asm_program.append("\tmov rax, 0x3c")
    asm_program.append("\tmov rdi, 0x0")
    asm_program.append("\tsyscall")

    if asm_program:
        return file_write_lines(output_file_name, asm_program,)
    return False

def parse_word_as_op(word: str):
    if (COUNT_OPS != 4):
        raise ExhaustiveHandling("in parse_word_as_op")

    if word == "+":
        return plus()
    elif word == "-":
        return minus()
    elif word == ".":
        return dump()
    else:
        return push(int(word))

def load_program_from_file(file_path) -> bool:
    with open(file_path, 'r') as f:
        return [parse_word_as_op(word) for word in f.read().split()]

def usage(program_name):
    print(f"Usage: {program_name} <SUBCOMMAND> [ARGS]")
    print("SUBCOMMANDS:")
    print("\tsim <file>\tSimulate the program.")
    print("\tcom <file>\tCompile the program.")

if __name__ == '__main__':
    argv = sys.argv
    program_name = argv.pop(0)
    if len(argv) < 1:
        usage(program_name)
        print("ERROR: no subcommand is provided")
        exit(1)
    subcommand = sys.argv.pop(0)

    if len(argv) < 1:
        print("ERROR: no input file.")
        exit(1)
    program_path = argv.pop(0)
    program_name = "".join(program_path.split('/')[-1].split('.')[0:-1])
    

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
    else:
        usage(program_name)
        print(f"ERROR: unknown subcommand {subcommand}")
