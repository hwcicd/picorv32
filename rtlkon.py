def rtlkon(filename):
    name = filename.split("/")[-1].split(".")[0]
    fptr = open(filename, "r")
    line = ""
    nonce = 1
    while "$scope" not in line:
        line = fptr.readline()
    vars = get_vars(fptr)
    vars_to_decls(vars, name)
    vals = {var: -1 for var in vars}
    assert("#0" in fptr.readline())
    assert("$dumpvars" in fptr.readline())
    dptr = open(name + ".dtrace", "w")
    while line:
        line, vals = tick(fptr, vals)
        vals_to_dtrace(vars, vals, nonce, dptr)
        nonce += 1


def get_vars(fptr):
    line = fptr.readline()
    vars = {} # just hope it stays ordered
    while "$enddefinitions" not in line:
        if "var" in line:
            parts = line.split()
            if parts[4] not in vars.values():
                vars[parts[3]] = parts[4]
        line = fptr.readline()
    return vars

def vars_to_decls(vars, name):
    f = open(name + ".decls", "w")
    def vars_to_tick(vars):
        for var in vars.values():
            f.write("  variable " + var + """
	var-kind variable
	rep-type int
	dec-type int
	comparability 1\n""")
    f.write("input-language C/C++\ndecl-version 2.0\n" +
            "var-comparability implicit\n\nppt ..tick():::ENTER\n" + 
            "  ppt-type enter\n")
    vars_to_tick(vars)    
    f.write("\nppt ..tick():::EXIT0\n" + 
            "  ppt-type subexit\n")
    vars_to_tick(vars)

def tick(fptr, vals):
    to_int = lambda val: int(val, 2) if val.isdigit() else -1 # x, z
    line = fptr.readline()
    while line and "#" != line[0]:
        # Two cases, words and bits
        if " " in line: # word
            val, var = line[1:].strip().split()
        else: # bit
            val, var = line[0], line[1:].strip()
        if var in vals:
            vals[var] = to_int(val)
        line = fptr.readline()
    return line, vals

def vals_to_dtrace(vars, vals, nonce, dptr):
    dptr.write("..tick():::ENTER\nthis_invocation_nonce\n" + str(nonce) + "\n")
    [dptr.write(vars[var] + "\n" + str(vals[var]) + "\n1\n") for var in vars]
    dptr.write("\n")
    dptr.write("..tick():::EXIT0\nthis_invocation_nonce\n" + str(nonce) + "\n")
    [dptr.write(vars[var] + "\n" + str(vals[var]) + "\n1\n") for var in vars]
    dptr.write("\n")

if __name__ == "__main__":
    import sys
    rtlkon(sys.argv[1])