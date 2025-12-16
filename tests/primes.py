def get_prime(n: int) -> int:
    candidate: int = 2
    found: int = 0
    while True:
        if is_prime(candidate):
            found = found + 1
            if found == n:
                return candidate
        candidate = candidate + 1
    return 0 # should never happen


def mod(a: int, b: int) -> int:
    q = a // b
    return a - q * b

def is_prime(x: int) -> bool:
    div: int = 2
    while div < x:
        if mod(x, div) == 0:
            return False
        div = div + 1
    return True


def start(n: int):
    i: int = 1
    while i <= n:
        print(get_prime(i))
        i = i + 1


start(10)
