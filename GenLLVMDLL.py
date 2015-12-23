# Generate an LLVM DLL from the LIB files that are built.
# Adapted from LLVMSharp's GenLLVMDLL.ps1 script.
# See LICENSE.txt for more details.
import getopt
import os
import re
import sys

MERGELIB = "MergeLLVM.lib"
LLVMLIB = "LLVM.lib"
DUMPOUT = "dumpbinoutput.txt"
EXPORTSDEF = "EXPORTS.DEF"

# Parse command line options.
filename = "libLLVM.dll"
arch = "X86"
options = getopt.getopt(sys.argv[1:], "", ["filename=", "arch="])[0]
for option in options:
	if option[0] == "--filename":
		filename = option[1]
	elif option[0] == "--arch":
		arch = option[1]

print "Please run from appropriate (x64/x86) Visual Studio Tools Command Prompt."
print "Generating {0} for architecture {1}".format(filename, arch)

def cleanup(fname):
	if os.path.isfile(fname):
		print "Cleaning up {}".format(fname)
		os.remove(fname);

cleanup(MERGELIB)
cleanup(LLVMLIB)

os.system("lib /OUT:{} LLVM*.lib".format(MERGELIB))
os.system("dumpbin /linkermember:1 {0} > {1}".format(MERGELIB, DUMPOUT))

exports = open(EXPORTSDEF, "w")
exports.write("EXPORTS\n\n")

p = None
if arch == "x64":
	p = re.compile(r"^\s+\w+\s+(LLVM.*)$")
else:
	p = re.compile(r"^\s+\w+\s+_(LLVM.*)$")

dumpbin = open(DUMPOUT, "r");
for line in dumpbin:
	m = p.match(line)
	if m is not None:
		exports.write(m.group(1) + "\n")
dumpbin.close()
exports.close()

os.system("link /dll /DEF:{0} /MACHINE:{1} /OUT:{2} {3}".format(
	EXPORTSDEF, arch, filename, MERGELIB))

cleanup(DUMPOUT)
cleanup(MERGELIB)
cleanup(EXPORTSDEF)