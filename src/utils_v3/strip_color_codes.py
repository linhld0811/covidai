#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


# regex
import re
Regex__ANSI_Escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)



def strip_color_codes(inp_string):
    return Regex__ANSI_Escape.sub('', inp_string)
