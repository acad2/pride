#!/usr/bin/env python
from __future__ import unicode_literals
import mpre._metapython
Shell = mpre._metapython.Shell
        
if __name__ == "__main__":
    metapython = mpre._metapython.Metapython(parse_args=True)
    metapython.start_machine()
    metapython.alert("shutting down", [metapython.instance_name], level='v')
    metapython.exit()