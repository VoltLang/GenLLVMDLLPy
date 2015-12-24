# Generate an LLVM DLL from the LIB files that are built.
# Adapted from LLVMSharp's GenLLVMDLL.ps1 script.
# See LICENSE.txt for more details.
#
# To use, build LLVM with Visual Studio, use the Visual Studio Command prompt
# to navigate to the directory with the .lib files (Debug\lib etc). Then run
#     python C:\Path\To\GenLLVMDLL.py LLVM*.lib
# If you're generating a 64 bit DLL, use the `--arch=x64` flag.
# You can use the --output flag to set the name of the new DLL.
# Generate the 64 bit DLL from the 64 bit prompt, 32 bit from the 32 bit prompt.
from tempfile import NamedTemporaryFile, mkstemp
from contextlib import contextmanager
from subprocess import check_call
import argparse
import os
import re


_ARCH_RE = {
    'x64': re.compile(r"^\s+\w+\s+(LLVM.*)$"),
    'x86': re.compile(r"^\s+\w+\s+_(LLVM.*)$")
}


@contextmanager
def removing(path):
    try:
        yield path
    finally:
        os.unlink(path)


def touch_tempfile(*args, **kwargs):
    fd, name = mkstemp(*args, **kwargs)
    os.close(fd)
    return name


def gen_llvm_dll(output, arch, libs, print_export):
    with removing(touch_tempfile(prefix='mergelib', suffix='.lib')) as mergelib, \
            removing(touch_tempfile(prefix='dumpout', suffix='.txt')) as dumpout, \
            removing(touch_tempfile(prefix='exports', suffix='.def')) as exports:

        lib_args = ['lib', '/OUT:{0}'.format(mergelib)]
        lib_args.extend(libs)
        check_call(lib_args)

        with open(dumpout, 'w+t') as dumpout_f:
            check_call(['dumpbin', '/linkermember:1', mergelib], stdout=dumpout_f)

        p = _ARCH_RE[arch]
        with open(exports, 'w+t') as exports_f:
            exports_f.write('EXPORTS\n\n')

            with open(dumpout) as dumpbin:
                for line in dumpbin:
                    m = p.match(line)
                    if m is not None:
                        exports_f.write(m.group(1) + '\n')
                        if print_export:
                            print m.group(1)

        check_call(['link',
                    '/dll',
                    '/DEF:{0}'.format(exports),
                    '/MACHINE:{0}'.format(arch),
                    '/OUT:{0}'.format(output),
                    mergelib])


def main():
    parser = argparse.ArgumentParser('GenLLVMDLL')

    parser.add_argument(
        '-o', '--output', help='output filename', default='libLLVM.dll'
    )
    parser.add_argument(
        '--arch', help='architecture', default='x86', choices=['x86', 'x64'], type=str.lower
    )
    parser.add_argument(
        'libs', metavar='LIBS', nargs='+', help='list of libraries to merge'
    )
    parser.add_argument(
        '--print-exports', help='print functions being exported to stdout', dest='print_export', action='store_true', default=False
    )

    ns = parser.parse_args()

    print 'Please run from appropriate (x64/x86) Visual Studio Tools Command Prompt.'
    print 'Generating {0} for architecture {1}'.format(ns.output, ns.arch)

    gen_llvm_dll(ns.output, ns.arch, ns.libs, ns.print_export)


if __name__ == '__main__':
    main()


