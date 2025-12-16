import subprocess
import sys
import json
from pathlib import Path

CHOCO_PARSER = Path( # chocopy parser path
    "/home/smubge/Documents/Cornell/CS6120/HW/final_proj/chocopy-bril/chocopy-python-compiler/main.py"
)

def parse_chocopy(src_path: str): # Parse ChocoPy source file to AST
    src_path = str(Path(src_path).resolve())
    out = subprocess.check_output(
        ["python3", str(CHOCO_PARSER), "--mode", "parse", "--print", src_path],
        text=True,
    )
    return json.loads(out)

class Compiler: # COmpiler class that builds up the IR
    def __init__(self):
        self.instrs = []
        self.var = 0
        self.lbl = 0

    def new_var(self):  # creates a new var
        t = f"t{self.var}"
        self.var += 1
        return t

    def new_label(self, base):  # creates a new label
        lbl = f"{base}_{self.lbl}"
        self.lbl += 1
        return lbl

    def addInstr(self, instr):  # adds instruction to the instruction list
        self.instrs.append(instr)

    def label(self, name):  # adds a label instruction
        self.instrs.append({"label": name})


BIN_OPS = {  # binary operations mapping
    "+": ("add", "int"),
    "-": ("sub", "int"),
    "*": ("mul", "int"),
    "//": ("div", "int"),
    "<": ("lt", "bool"),
    "<=": ("le", "bool"),
    ">": ("gt", "bool"),
    ">=": ("ge", "bool"),
    "==": ("eq", "bool"),
}


def extract_return_type(fn):  # extracts return type from function definition
    ret_type = fn.get("returnType")
    if ret_type is None:
        return None
    if ret_type.get("kind") == "ClassType":
        cn = ret_type.get("className")
        if cn == "int":
            return "int"
        if cn == "bool":
            return "bool"
        if cn == "<None>":
            return None
    return None


def last_op(instrs):  # gets the last operation in the instruction list
    for i in reversed(instrs):
        if "op" in i:
            return i["op"]
    return None


def compile_mod(a, b, builder):  # compiles modulus operation
    q = builder.new_var()
    t = builder.new_var()
    r = builder.new_var()
    builder.addInstr({"op": "div", "dest": q, "type": "int", "args": [a, b]})
    builder.addInstr({"op": "mul", "dest": t, "type": "int", "args": [q, b]})
    builder.addInstr({"op": "sub", "dest": r, "type": "int", "args": [a, t]})
    return r


def compile_short_circuit(op, expr, env, b, fn_rets):  # compiles short-circuiting logical operations
    left, _ = compile_expr(expr["left"], env, b, fn_rets)
    out = b.new_var()
    rhs = b.new_label("rhs")
    end = b.new_label("end")

    if op == "and":
        b.addInstr({"op": "const", "dest": out, "type": "bool", "value": False})
        b.addInstr({"op": "br", "args": [left], "labels": [rhs, end]})
    else:
        b.addInstr({"op": "const", "dest": out, "type": "bool", "value": True})
        b.addInstr({"op": "br", "args": [left], "labels": [end, rhs]})

    b.label(rhs)
    right, _ = compile_expr(expr["right"], env, b, fn_rets)
    b.addInstr({"op": "id", "dest": out, "type": "bool", "args": [right]})
    b.addInstr({"op": "jmp", "labels": [end]})
    b.label(end)
    return out, "bool"


def compile_not(v, b):  # compiles the NOT op
    out = b.new_var()
    t_lbl = b.new_label("not_t")
    f_lbl = b.new_label("not_f")
    end = b.new_label("not_end")

    b.addInstr({"op": "br", "args": [v], "labels": [t_lbl, f_lbl]})

    b.label(t_lbl)
    b.addInstr({"op": "const", "dest": out, "type": "bool", "value": False})
    b.addInstr({"op": "jmp", "labels": [end]})

    b.label(f_lbl)
    b.addInstr({"op": "const", "dest": out, "type": "bool", "value": True})
    b.addInstr({"op": "jmp", "labels": [end]})

    b.label(end)
    return out, "bool"


def compile_expr(expr, env, b, fn_rets): # compiles expressions
    k = expr["kind"]

    if k == "IntegerLiteral":
        t = b.new_var()
        b.addInstr({"op": "const", "dest": t, "type": "int", "value": expr["value"]})
        return t, "int"

    if k == "BooleanLiteral":
        t = b.new_var()
        b.addInstr({"op": "const", "dest": t, "type": "bool", "value": expr["value"]})
        return t, "bool"

    if k == "Identifier":
        return env[expr["name"]]

    if k == "UnaryExpr":
        v, _ = compile_expr(expr["operand"], env, b, fn_rets)
        return compile_not(v, b)

    if k == "BinaryExpr":
        op = expr["operator"]

        if op in ("and", "or"):
            return compile_short_circuit(op, expr, env, b, fn_rets)

        l, _ = compile_expr(expr["left"], env, b, fn_rets)
        r, _ = compile_expr(expr["right"], env, b, fn_rets)

        if op == "%":
            t = compile_mod(l, r, b)
            return t, "int"

        if op == "!=":
            eqt = b.new_var()
            b.addInstr({"op": "eq", "dest": eqt, "type": "bool", "args": [l, r]})
            return compile_not(eqt, b)

        bop, ty = BIN_OPS[op]
        t = b.new_var()
        b.addInstr({"op": bop, "dest": t, "type": ty, "args": [l, r]})
        return t, ty

    if k == "CallExpr":
        fname = expr["function"]["name"]
        args = [compile_expr(a, env, b, fn_rets)[0] for a in expr["args"]]
        ret_ty = fn_rets.get(fname)
        if ret_ty is None:
            b.addInstr({"op": "call", "funcs": [fname], "args": args})
            return None, "void"
        t = b.new_var()
        b.addInstr({"op": "call", "dest": t, "type": ret_ty, "funcs": [fname], "args": args})
        return t, ret_ty

    raise NotImplementedError(k)


def compile_stmt(stmt, env, b, fn_rets):  # compiles statements
    k = stmt["kind"]

    if k == "VarDef":
        name = stmt["var"]["identifier"]["name"]
        val, typing = compile_expr(stmt["value"], env, b, fn_rets)
        b.addInstr({"op": "id", "dest": name, "type": typing, "args": [val]})
        env[name] = (name, typing)
        return

    if k == "AssignStmt":
        name = stmt["targets"][0]["name"]
        val, typing = compile_expr(stmt["value"], env, b, fn_rets)
        b.addInstr({"op": "id", "dest": name, "type": typing, "args": [val]})
        env[name] = (name, typing)
        return

    if k == "ExprStmt":
        exp = stmt["expr"]
        if exp["kind"] == "CallExpr":
            fname = exp["function"]["name"]
            args = [compile_expr(a, env, b, fn_rets)[0] for a in exp["args"]]
            if fname == "print":
                b.addInstr({"op": "print", "args": args})
            else:
                b.addInstr({"op": "call", "funcs": [fname], "args": args})
        return

    if k == "ReturnStmt":
        if stmt["value"] is None:
            b.addInstr({"op": "ret"})
        else:
            val, _ = compile_expr(stmt["value"], env, b, fn_rets)
            b.addInstr({"op": "ret", "args": [val]})
        return

    if k == "IfStmt":
        cond, _ = compile_expr(stmt["condition"], env, b, fn_rets)
        then = b.new_label("then")
        exp = b.new_label("else")
        end = b.new_label("ifend")

        b.addInstr({"op": "br", "args": [cond], "labels": [then, exp]})

        b.label(then)
        for s in stmt["thenBody"]:
            compile_stmt(s, env, b, fn_rets)
        b.addInstr({"op": "jmp", "labels": [end]})

        b.label(exp)
        for s in stmt.get("elseBody", []):
            compile_stmt(s, env, b, fn_rets)
        b.addInstr({"op": "jmp", "labels": [end]})

        b.label(end)
        return

    if k == "WhileStmt":
        head = b.new_label("loop")
        body = b.new_label("body")
        end = b.new_label("end")

        b.label(head)
        cond, _ = compile_expr(stmt["condition"], env, b, fn_rets)
        b.addInstr({"op": "br", "args": [cond], "labels": [body, end]})

        b.label(body)
        for s in stmt["body"]:
            compile_stmt(s, env, b, fn_rets)
        b.addInstr({"op": "jmp", "labels": [head]})

        b.label(end)
        return

    raise NotImplementedError(k)


def compile_function(func, func_returns):  # compiles function definitions
    b = Compiler()
    env = {}
    args = []
    ret_ty = extract_return_type(func)

    for p in func.get("params", []):
        name = p["identifier"]["name"]
        args.append({"name": name, "type": "int"})
        env[name] = (name, "int")

    for d in func.get("declarations", []):
        if d["kind"] == "VarDef":
            compile_stmt(d, env, b, func_returns)

    for s in func.get("statements", []):
        compile_stmt(s, env, b, func_returns)

    if last_op(b.instrs) != "ret":
        if ret_ty is None:
            b.addInstr({"op": "ret"})
        else:
            z = b.new_var()
            b.addInstr({"op": "const", "dest": z, "type": ret_ty, "value": False if ret_ty == "bool" else 0})
            b.addInstr({"op": "ret", "args": [z]})

    out = {"name": func["name"]["name"], "args": args, "instrs": b.instrs}
    if ret_ty is not None:
        out["type"] = ret_ty
    return out


def compile_ast(ast): # compiles the entire AST
    declarat = ast.get("declarations", [])

    func_returns = {
        d["name"]["name"]: extract_return_type(d)
        for d in declarat
        if d.get("kind") == "FuncDef"
    }

    functions = [
        compile_function(d, func_returns)
        for d in declarat
        if d.get("kind") == "FuncDef"
    ]

    b = Compiler()
    env = {}

    for d in declarat:
        if d.get("kind") == "VarDef":
            compile_stmt(d, env, b, func_returns)

    for s in ast.get("statements", []):
        compile_stmt(s, env, b, func_returns)

    b.addInstr({"op": "ret"})
    functions.append({"name": "main", "args": [], "instrs": b.instrs})
    return {"functions": functions}

ast = parse_chocopy(sys.argv[1])
print(json.dumps(compile_ast(ast), indent=2))

