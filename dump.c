
#include <stdio.h>
#include <stdint.h>
#include <unistd.h>

#define BUF_CAP 32

void dump(uint64_t number)
{
    int i;
    char buf[BUF_CAP];
    buf[BUF_CAP-1] = '\n';
    
    i = BUF_CAP - 2;
    do {
        i--;
        printf("[dbg] %ld\n", number);
        buf[i] = number % 10 + '0';
        number /= 10;
    } while (number > 0);
    write(1, &buf[i], BUF_CAP - i);
}

int main(int argc, char *argv[])
{
    dump(1234500004300);
    dump(3);
    return 0;
}
