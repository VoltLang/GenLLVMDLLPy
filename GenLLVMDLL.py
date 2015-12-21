# Generate an LLVM DLL from the LIB files that are built.
# Adapted from LLVMSharp's GenLLVMDLL.ps1 script.
# See LICENSE.txt for more details.
import os
import sys
import getopt

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

print "!!!! Please run from appropriate (i.e. x64 or x86) Visual Studio Tools Command Prompt !!!!"
print "!!!! Generating for architecture --> {} !!!!".format(arch)
print "*** Generating LLVM Shared DLL {0} for Architecture {1} ***".format(filename, arch)

def cleanup(fname):
	if os.path.isfile(fname):
		print "Cleaning up {}".format(fname)
		os.remove(fname);

cleanup(MERGELIB)
cleanup(LLVMLIB)

os.system("lib /OUT:{} LLVM*.lib".format(MERGELIB))
os.system("dumpbin /linkermember:1 {0} > {1}".format(MERGELIB, DUMPOUT))

exports = open(EXPORTSDEF, "w")
exports.write("EXPORTS\n\n");
