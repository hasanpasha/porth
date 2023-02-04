#!/usr/bin/env python3

import sys
import subprocess
from argparse import ArgumentParser
from os import path

class Unreachable(Exception):
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
OP_IF = iota()
OP_END = iota()
OP_ELSE = iota()
OP_DUP = iota()
OP_GT = iota()
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

def iff():
    return (OP_IF, )

def end():
    return (OP_END, )

def elze():
    return (OP_ELSE, )

def dup():
    return (OP_DUP, )

def gt():
    return (OP_GT, )

def call_cmd(cmd, verbose=False):
    if verbose:
        print("[CMD] ", " ".join(cmd))
    subprocess.run(cmd)

def file_write_lines(file_name, lines: list) -> bool:
    with open(file_name, "w") as output:
        for line in lines:
            if output.write(line + '\n') != (len(line)+1):
                return False
        else:
            return True

def lines_from_file(file_name) -> list:
    with open(file_name, 'r') as f:
        lines = f.readlines()
        for i in range(0, len(lines)):
            lines[i] = lines[i].replace('\n', '')
    return lines


def simulate_program(program):
    stack = []
    ip = 0
    while ip < len(program):
        if COUNT_OPS != 10: 
            raise ExhaustiveHandling()
        op = program[ip]
        if op[0] == OP_PUSH:
            stack.append(op[1])
            ip += 1
        elif op[0] == OP_PLUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(a + b)
            ip += 1
        elif op[0] == OP_MINUS:
            a = stack.pop()
            b = stack.pop()
            stack.append(b - a)
            ip += 1
        elif op[0] == OP_DUP:
            a = stack.pop()
            stack.append(a)
            stack.append(a)
            ip += 1
        elif op[0] == OP_DUMP:
            a = stack.pop()
            print(a)
            ip += 1
        elif op[0] == OP_EQUAL:
            a = stack.pop()
            b = stack.pop()
            stack.append(int(a == b))
            ip += 1
        elif op[0] == OP_GT:
            b = stack.pop()
            a = stack.pop()
            stack.append(int(a > b))
            ip += 1
        elif op[0] == OP_IF:
            a = stack.pop()
            if a == 0:
                assert len(op) >= 2, "`if` instruction does not have a reference to the end of its block. Please call crossreference_program() on the program before trying to simulate it."
                ip = op[1]
            else:
                ip += 1
        elif op[0] == OP_ELSE:
            assert len(op) >= 2, "`else` instruction does not have a reference to the end of its block. Please call crossreference_program() on the program before trying to simulate it."
            assert ip != op[1], "OOPS!!"
            ip = op[1]
        elif op[0] == OP_END:
            ip += 1
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
    for ip in range(len(program)):
        if COUNT_OPS != 10: 
            raise ExhaustiveHandling()
        op = program[ip]
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
        elif op[0] == OP_DUP:
            asm_program.append("\t;; -- dup --")
            asm_program.append("\tpop rax");
            asm_program.append("\tpush rax");
            asm_program.append("\tpush rax");
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
        elif op[0] == OP_GT:
            asm_program.append("\t;; -- greator --")
            asm_program.append("\tmov rcx, 0")
            asm_program.append("\tmov rdx, 1")
            asm_program.append("\tpop rax")
            asm_program.append("\tpop rbx")
            asm_program.append("\tcmp rbx, rax")
            asm_program.append("\tcmovg rcx, rdx")
            asm_program.append("\tpush rcx")
        elif op[0] == OP_IF:
            asm_program.append("\t;; -- if --")
            asm_program.append("\tpop rax")
            asm_program.append("\ttest rax, rax")
            assert len(op) >= 2, "`if` instruction does not have a reference to the end of its block. Please call crossreference_program() on the program before trying to compile it."
            asm_program.append(f"\tjz addr_{op[1]}")
        elif op[0] == OP_ELSE:
            assert len(op) >= 2, "`else` instruction does not have a reference to the end of its block. Please call crossreference_program() on the program before trying to compile it."
            asm_program.append("\t;; -- else --")
            asm_program.append(f"\tjmp addr_{op[1]}")
            asm_program.append(f"addr_{ip+1}:")
        elif op[0] == OP_END:
            asm_program.append(f"addr_{ip}:")
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

    if (COUNT_OPS != 10):
        raise ExhaustiveHandling("in parse_word_as_op")

    if word == "+":
        return plus()
    elif word == "-":
        return minus()
    elif word == ".":
        return dump()
    elif word == "=":
        return equal()
    elif word == "if":
        return iff()
    elif word == "end":
        return end()
    elif word == "else":
        return elze()
    elif word == "dup":
        return dup()
    elif word == ">":
        return gt()
    else:
        try:
            return push(int(word))
        except ValueError as err:
            print(f"{file_path}:{row}:{col}: {err}")
            exit(1)

def crossreference_program(program):
    stack = []
    for ip in range(len(program)):
        op = program[ip]
        if COUNT_OPS != 10:
            raise ExhaustiveHandling("in crossreference_program. Keep in mind that not all of the ops need to be handled in here, only thos that form blocks.")
        if op[0] == OP_IF:
            stack.append(ip)
        elif op[0] == OP_ELSE:
            if_ip = stack.pop()
            assert program[if_ip][0] == OP_IF, "`else` can only close `if` for now"
            program[if_ip] = (OP_IF, ip+1)
            stack.append(ip)
        elif op[0] == OP_END:
            block_ip = stack.pop()
            if program[block_ip][0] == OP_IF or program[block_ip][0] == OP_ELSE:
                program[block_ip] = (program[block_ip][0], ip)
            else:
                assert False, "`end` can only close `if-else` for now"
    return program

def find_col(line, start, predicate):
    while start < len(line) and not predicate(line[start]):
        start += 1
    return start

def lex_line(line):
    col = find_col(line, 0, lambda x: not x.isspace())
    while col < len(line):
        if line[col] == "#":
            break
        col_end = find_col(line, col, lambda x: x.isspace())
        yield (col, line[col:col_end])
        col = find_col(line, col_end, lambda x: not x.isspace())

def lex_file(file_path) -> list:
    with open(file_path, 'r') as f:
        for (row, line) in enumerate(f.readlines()):
            for (col, token) in lex_line(line):
                yield (file_path, row, col, token, )

def load_program_from_file(file_path):
    return crossreference_program([parse_word_as_op(token) for token in lex_file(file_path)])

def get_args():
    parser = ArgumentParser(description="Porth language compiler.")
    
    subparser = parser.add_subparsers(help="select mode", dest="subcommand")
    sim_parse = subparser.add_parser("sim", help="Simulate the program.")
    com_parse = subparser.add_parser("com", help="Compile the program.")
    com_parse.add_argument("-r", "--run", action="store_true",
                           help="run the generated executable.")
    com_parse.add_argument("-o", "--output", type=str,
                           help="output path.")
    com_parse.add_argument("-v", "--verbose", action="store_true",
                           help="set verbosity.")

    
    parser.add_argument("file_path", metavar="file_path", type=str,
                        help="The input file path")
    return parser.parse_args()

def get_file_info(source_path):
    source_abs_path = path.abspath(source_path)
    head, source_file = path.split(source_abs_path)
    return (source_abs_path, head, source_file)

if __name__ == '__main__':
    command_arguments = get_args()
    source_path = command_arguments.file_path
    subcommand = command_arguments.subcommand
    
    source_abs_path, path_head, source_file = get_file_info(source_path)
    
    program = load_program_from_file(source_abs_path)
    if not program:
        exit(1)

    if subcommand == "sim":
        simulate_program(program)

    elif subcommand == "com":
        com_run = command_arguments.run
        com_output = command_arguments.output
        com_verbose = command_arguments.verbose

        asm_path = path.join(path_head, f"{source_file}.asm")
        object_path = path.join(path_head, f"{source_file}.o")
        if com_output: 
            exe_path, _, _ = get_file_info(com_output)
        else:
            exe_path = path.join(path_head, f"{source_file}.exe")

        compile_program(program, asm_path)
        call_cmd(["nasm", "-felf64", asm_path, ], verbose=com_verbose)
        call_cmd(["ld", "-o", exe_path, object_path, ], verbose=com_verbose)
        if com_run:
            call_cmd([exe_path], verbose=com_verbose)
