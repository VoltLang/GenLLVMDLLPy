# Generate an LLVM DLL from the LIB files that are built.
# Adapted from LLVMSharp's GenLLVMDLL.ps1 script.
# See LICENSE.txt for more details.
import getopt
import os
import re
import sys
import tempfile

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

mergelib = tempfile.NamedTemporaryFile(prefix = "mergelib", suffix = ".lib", delete = False)
mergelib.close()
dumpout = tempfile.NamedTemporaryFile(prefix = "dumpout", suffix = ".txt", mode = "w+t", delete = False)
dumpout.close()
exports = tempfile.NamedTemporaryFile(prefix = "exports", suffix = ".def", mode = "w+t", delete = False)

os.system("lib /OUT:{} LLVM*.lib".format(mergelib.name))
os.system("dumpbin /linkermember:1 {0} > {1}".format(mergelib.name, dumpout.name))

exports.write("EXPORTS\n\n")

p = None
if arch == "x64":
	p = re.compile(r"^\s+\w+\s+(LLVM.*)$")
else:
	p = re.compile(r"^\s+\w+\s+_(LLVM.*)$")

dumpbin = open(dumpout.name, "r");
for line in dumpbin:
	m = p.match(line)
	if m is not None:
		exports.write(m.group(1) + "\n")
dumpbin.close()
exports.close()

os.system("link /dll /DEF:{0} /MACHINE:{1} /OUT:{2} {3}".format(
	exports.name, arch, filename, mergelib.name))

os.unlink(dumpout.name)
os.unlink(mergelib.name)
os.unlink(exports.name)