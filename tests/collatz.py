def collatz(n: int):
    while n != 1:
        print(n)
        if n % 2 == 0:
            n = n // 2
        else:
            n = 3*n + 1
    print(n)

def start(n: int):
    collatz(n)

start(7)
