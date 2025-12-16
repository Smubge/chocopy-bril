def geta(a: int) -> int:
    return a


def f(i: int, x: int, a: int) -> int:
    if i <= 0:
        return geta(a)
    else:
        a = a * x
        return f(i - 1, x, a)


def exp(x: int, y: int) -> int:
    a: int = 1
    return f(y, x, a)


n: int = 42
i: int = 0

while i <= n:
    print(exp(2, i % 31))
    i = i + 1

