"""Disassemble arm64 methods of game/Cygnus, naming the selectors, imported
functions, classes and strings each instruction refers to. Needs capstone
(pip install capstone); nothing else in the repo does.

    python tools/dis64.py CCSoundManager playBackgroundMedium:
    python tools/dis64.py --list CCSoundManager      the class's methods
    python tools/dis64.py --at 0x100024ed8           code at an address, such as a block

A class method is named with a + in front, such as +shared. Output stops at
the first ret, so a method that continues past one shows only its first part.
"""
import sys

from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM
import macho64 as M

SEL = M.selrefs()
STUB = M.stubs()
IMPS = {}
for name, inst, cls in M.classes():
    for s, i in inst:
        IMPS[(name, s)] = i
    for s, i in cls:
        IMPS[(name, "+" + s)] = i
BY_ADDR = {v: "%s %s" % k for k, v in IMPS.items()}

classrefs = {}
if "__DATA,__objc_classrefs" in M.sections:
    a, size, _ = M.sections["__DATA,__objc_classrefs"]
    for k in range(size // 8):
        target = M.u64(a + k * 8)
        name = None
        if target:
            try:
                name = M.read_class(target, False)[0]
            except Exception:
                name = None
        classrefs[a + k * 8] = name or STUB.get(a + k * 8) or "class@%x" % target

cfstr = {}
if "__DATA,__cfstring" in M.sections:
    a, size, _ = M.sections["__DATA,__cfstring"]
    for k in range(size // 32):
        cfstr[a + k * 32] = M.cstr(M.u64(a + k * 32 + 16))

md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)


def name_of(addr):
    for table in (SEL, classrefs, cfstr, STUB):
        if addr in table:
            v = table[addr]
            if table is SEL:
                return "sel:" + str(v)
            if table is cfstr:
                return '@"%s"' % v
            return str(v)
    if addr in BY_ADDR:
        return BY_ADDR[addr]
    return None


def dis(start, limit=600):
    code = M.m[M.va2off(start):M.va2off(start) + limit * 4]
    regs = {}
    for ins in md.disasm(code, start):
        note = ""
        ops = ins.op_str
        if ins.mnemonic == "adrp":
            r, imm = ops.split(", ")
            regs[r] = int(imm.strip("#"), 16)
        elif ins.mnemonic in ("ldr", "add") and "#" in ops:
            parts = [p.strip() for p in ops.replace("[", "").replace("]", "").split(",")]
            dst, base = parts[0], parts[1]
            imm = int(parts[-1].strip("#"), 0) if parts[-1].startswith("#") else 0
            if base in regs:
                addr = regs[base] + imm
                n = name_of(addr)
                if n:
                    note = n
                if ins.mnemonic == "add":
                    regs[dst] = addr
        elif ins.mnemonic in ("bl", "b"):
            target = int(ops.strip("#"), 16)
            n = name_of(target)
            if n:
                note = n
        print("  %x: %-6s %-34s %s" % (ins.address, ins.mnemonic, ops, ("; " + note) if note else ""))
        if ins.mnemonic == "ret":
            break
        if ins.mnemonic == "b" and not note.startswith("_objc"):
            # A tail branch out of the method ends it, unless it stays inside.
            target = int(ops.strip("#"), 16)
            if target < start or target > start + limit * 4:
                break


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["--list"]:
        for (cls, sel), imp in sorted(IMPS.items(), key=lambda kv: kv[1]):
            if cls == args[1]:
                print("%x %s" % (imp, sel))
        sys.exit()
    if args[:1] == ["--at"]:
        dis(int(args[1], 16))
        sys.exit()
    for k in range(0, len(args), 2):
        key = (args[k], args[k + 1])
        print("=== -[%s %s] at %x" % (key[0], key[1], IMPS[key]))
        dis(IMPS[key])
