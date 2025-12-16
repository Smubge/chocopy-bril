def sqrt(s: int) -> int:

    x0: int = 0
    x1: int = 0

    if s <= 1:
        return s

    x0 = s // 2
    x1 = (x0 + s // x0) // 2

    while x1 < x0:
        x0 = x1
        x1 = (x0 + s // x0) // 2

    return x0

def quadratic(a: int, b: int, c: int):

    Y: int = 0
    X: int = 0

    Y = sqrt(b*b - 4*a*c)
    X = 0-b

    print((X + Y) // (2 * a))
    print((X - Y) // (2 * a))


quadratic(1, 2, 3)


