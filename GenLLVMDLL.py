# Generate an LLVM DLL from the LIB files that are built.
# Adapted from LLVMSharp's GenLLVMDLL.ps1 script.
# See LICENSE.txt for more details.
import sys
import getopt

# Parse command line options.
filename = "libLLVM.dll"
arch = "X86"
options = getopt.getopt(sys.argv[1:], "", ["filename=", "arch="])[0]
for option in options:
	if option[0] == "--filename":
		filename = option[1]
	elif option[0] == "--arch":
		arch = option[1]
