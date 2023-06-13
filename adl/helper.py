"""
dataloader-Hilfsfunktionen
"""

import re

def remove_escaping(string, escaped_char=r'"'):
    escape_pattern = re.compile(r'[\\](' + escaped_char + r')')
    return escape_pattern.sub(r'\1', string)

def run_re(expression, re_pipeline):
    if re_pipeline:
        first_sub = re.sub(re_pipeline[0][0], re_pipeline[0][1], expression)
        sub_expression = run_re(first_sub, re_pipeline[1:])
    else:
        sub_expression = expression
    return sub_expression
