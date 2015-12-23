# Generate an LLVM DLL from the LIB files that are built.
# Adapted from LLVMSharp's GenLLVMDLL.ps1 script.
# See LICENSE.txt for more details.
from tempfile import NamedTemporaryFile, mkstemp
from contextlib import contextmanager
from subprocess import check_call
import argparse
import os
import re


_ARCH_RE = {
    'x64': re.compile(r"^\s+\w+\s+(LLVM.*)$"),
    'X86': re.compile(r"^\s+\w+\s+_(LLVM.*)$")
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


def gen_llvm_dll(output, arch, libs):
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
        '--arch', help='architecture', default='X86', choices=['x86', 'x64'], type=str.lower
    )
    parser.add_argument(
        'libs', metavar='LIBS', nargs='+', help='list of libraries to merge'
    )

    ns = parser.parse_args()

    print 'Please run from appropriate (x64/x86) Visual Studio Tools Command Prompt.'
    print 'Generating {0} for architecture {1}'.format(ns.output, ns.arch)

    gen_llvm_dll(ns.output, ns.arch, ns.libs)


if __name__ == '__main__':
    main()


