#!/bin/sh

set -xe 

nasm -felf64 hello_world.asm &&
ld -o hello_world hello_world.o
