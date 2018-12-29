#!/usr/bin/env python3
from io import StringIO
from subprocess import Popen, PIPE
import sys

with Popen(['python', sys.argv[1]], stderr=PIPE, bufsize=1,
           universal_newlines=True) as p, StringIO() as buf:
    for line in p.stderr:
        print(line, end='')
        buf.write(line)
    output = buf.getvalue()
    print(output)
rc = p.returncode