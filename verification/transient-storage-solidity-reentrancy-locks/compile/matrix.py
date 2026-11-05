#!/usr/bin/env python3
"""Compile small snippets with several solc releases, legacy and via-IR.

Binaries are read from ~/.svm/<v>/solc-<v>. Prints accept/reject with the error code.
"""
import json, os, subprocess, tempfile

VERSIONS = ["0.8.23", "0.8.24", "0.8.26", "0.8.27", "0.8.28", "0.8.33", "0.8.34", "0.8.36", "0.8.38"]
H = "// SPDX-License-Identifier: MIT\npragma solidity >=0.8.0;\n"

CASES = {
    "yul tstore": "contract C { function f() external { assembly { tstore(0, 1) } } }",
    "uint transient": "contract C { uint256 transient x; function f() external { x = 1; } }",
    "bool, public getter": "contract C { bool public transient x; }",
    "transient before visibility": "contract C { uint256 transient public x; }",
    "address, enum, UDVT, bytes32, contract, function": """
        type U is uint64; enum E { A, B } interface I {}
        contract C { address transient a; E transient e; U transient u; bytes32 transient b; I transient i;
                     function () external transient f; }""",
    "delete on transient": "contract C { uint256 transient x; function f() external { x = 1; delete x; } }",
    "name `transient` for a storage variable": "contract C { uint256 transient; }",
    "mapping": "contract C { mapping(address => uint256) transient m; }",
    "fixed array": "contract C { uint256[2] transient a; }",
    "dynamic array": "contract C { uint256[] transient a; }",
    "bytes": "contract C { bytes transient b; }",
    "string": "contract C { string transient s; }",
    "struct": "contract C { struct S { uint256 a; } S transient s; }",
    "local variable": "contract C { function f() external pure { uint256 transient x; x; } }",
    "parameter": "contract C { function f(uint256 transient x) external pure {} }",
    "initializer": "contract C { uint256 transient x = 1; }",
    "constant": "contract C { uint256 constant transient x = 1; }",
    "immutable": "contract C { uint256 immutable transient x; }",
    "write in view": "contract C { uint256 transient x; function f() external view { x = 1; } }",
    "read in pure": "contract C { uint256 transient x; function f() external pure returns (uint256) { return x; } }",
    "read in view": "contract C { uint256 transient x; function f() external view returns (uint256) { return x; } }",
    "file-level": "uint256 transient x;",
    "library state variable": "library L { uint256 transient x; }",
    "reference to a transient variable (.slot in assembly)": """
        contract C { uint256 transient x; function f() external { assembly { tstore(x.slot, 1) } } }""",
}

def solc(v):
    return os.path.expanduser(f"~/.svm/{v}/solc-{v}")

def compile_one(v, src, ir, evm):
    if not os.path.exists(solc(v)):
        return "no binary"
    # solc 0.8.23 does not know the name "cancun"; shanghai is its newest target.
    if v == "0.8.23" and evm == "cancun":
        evm = "shanghai"
    settings = {"evmVersion": evm, "viaIR": ir, "optimizer": {"enabled": True},
                "outputSelection": {"*": {"*": ["evm.bytecode.object"]}}}
    inp = {"language": "Solidity", "sources": {"a.sol": {"content": H + src}}, "settings": settings}
    p = subprocess.run([solc(v), "--standard-json"], input=json.dumps(inp), capture_output=True, text=True)
    try:
        o = json.loads(p.stdout)
    except ValueError:
        return "crash"
    errs = [e for e in o.get("errors", []) if e["severity"] == "error"]
    if errs:
        e = errs[0]
        return f"{e['type']} {e.get('errorCode')}"
    return "ok"

w = max(len(k) for k in CASES)
print("case".ljust(w), *[v.ljust(20) for v in VERSIONS])
for name, src in CASES.items():
    row = []
    for v in VERSIONS:
        a, b = compile_one(v, src, False, "cancun"), compile_one(v, src, True, "cancun")
        row.append((a if a == b else f"{a}/{b}"[:20]).ljust(20))
    print(name.ljust(w), *row)

print()
print("target below cancun, 0.8.38 and 0.8.28, legacy:")
for v in ("0.8.28", "0.8.38"):
    for name in ("uint transient", "yul tstore"):
        print(v, name, "shanghai:", compile_one(v, CASES[name], False, "shanghai"))

print()
print("warnings, 0.8.38 (legacy):")
for name, src in {
    "assembly tstore": CASES["yul tstore"],
    "high-level transient write": CASES["uint transient"],
    "name `transient`": CASES["name `transient` for a storage variable"],
}.items():
    inp = {"language": "Solidity", "sources": {"a.sol": {"content": H + src}},
           "settings": {"evmVersion": "cancun", "outputSelection": {"*": {"*": ["evm.bytecode.object"]}}}}
    p = subprocess.run([solc("0.8.38"), "--standard-json"], input=json.dumps(inp), capture_output=True, text=True)
    for e in json.loads(p.stdout).get("errors", []):
        if e["severity"] == "warning" and e.get("errorCode") != "2018":
            print(f"{name}: {e.get('errorCode')} {e['message'][:200]}")
    print(f"{name}: done")
