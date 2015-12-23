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


def gen_llvm_dll(filename, arch):
    with removing(touch_tempfile(prefix='mergelib', suffix='.lib')) as mergelib, \
            removing(touch_tempfile(prefix='dumpout', suffix='.txt', text=True)) as dumpout:
        check_call(['lib', '/OUT:{0}'.format(mergelib), 'LLVM*.lib'])
        check_call(['dumpbin', '/linkermember:1', mergelib, '>', dumpout])

        p = _ARCH_RE[arch]

        with NamedTemporaryFile(prefix='exports', suffix='.def', mode='w+t') as exports:
            exports.write('EXPORTS\n\n')

            with open(dumpout) as dumpbin:
                for line in dumpbin:
                    m = p.match(line)
                    if m is not None:
                        exports.write(m.group(1) + '\n')

            check_call(['link',
                        '/dll',
                        '/DEF:{0}'.format(exports.name),
                        '/MACHINE:{0}'.format(arch),
                        '/OUT:{1}'.format(filename),
                        mergelib])


def main():
    parser = argparse.ArgumentParser('GenLLVMDLL')

    parser.add_argument(
        '--filename', help='output filename', default='libLLVM.dll'
    )
    parser.add_argument(
        '--arch', help='architecture', default='X86', choices=['X86', 'x64']
    )

    ns = parser.parse_args()

    print 'Please run from appropriate (x64/x86) Visual Studio Tools Command Prompt.'
    print 'Generating {0} for architecture {1}'.format(ns.filename, ns.arch)

    gen_llvm_dll(ns.filename, ns.arch)


if __name__ == '__main__':
    main()


