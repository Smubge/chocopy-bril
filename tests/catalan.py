def catalan(n: int) -> int:
    i: int = 0
    c: int = 1
    if n == 0 or n == 1:
        return c
    c = 0
    while i < n:
        c = c + catalan(i) * catalan(n - i - 1)
        i = i + 1
    return c

def start(n: int):
    print(catalan(n))

start(5)
