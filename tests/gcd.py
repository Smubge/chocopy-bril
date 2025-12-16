def mod(u: int, v: int) -> int:
    return u - (u // v) * v


def gcd1(u: int, v: int) -> int:
    t: int = 0

    if u == 0:
        return v
    elif v == 0:
        return u
    elif mod(u, 2) == 0 and mod(v, 2) == 0:
        return 2 * gcd1(u // 2, v // 2)
    elif mod(v, 2) == 0:
        return gcd1(u, v // 2)
    else:
        if u > v:
            t = u
            u = v
            v = t
        return gcd1(u, v - u)


def gcd2(u: int, v: int) -> int:
    t: int = 0
    k: int = 1

    if u == 0:
        return v
    if v == 0:
        return u

    while mod(u, 2) == 0 and mod(v, 2) == 0:
        k = k * 2
        u = u // 2
        v = v // 2

    while u > 0 and mod(u, 2) == 0:
        u = u // 2

    while v > 0 and mod(v, 2) == 0:
        v = v // 2

    while True:
        if u > v:
            t = u
            u = v
            v = t

        v = v - u

        if v == 0:
            return u * k

        while v > 0 and mod(v, 2) == 0:
            v = v // 2


def gcd3(u: int, v: int) -> int:
    while not u == v:
        if u > v:
            u = u - v
        else:
            v = v - u
    return u


def gcd4(u: int, v: int) -> int:
    if v == 0:
        return u
    else:
        return gcd4(v, mod(u, v))


def gcd5(u: int, v: int) -> int:
    t: int = 0
    while not v == 0:
        t = u
        u = v
        v = mod(t, v)
    return u


a: int = 1
b: int = 2
v: int = 3

if v == 1:
    print(gcd1(a, b))
elif v == 2:
    print(gcd2(a, b))
elif v == 3:
    print(gcd3(a, b))
elif v == 4:
    print(gcd4(a, b))
elif v == 5:
    print(gcd5(a, b))

