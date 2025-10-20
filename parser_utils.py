# parser_utils.py
import re

def tokenize(text):
    """
    Breaks the SECS message text into a stream of tokens.
    This version correctly extracts only the value, not the full tag.
    """
    token_specification = [
        ('LIST_START', r'<\s*L\s*\[\d+\]\s*>'),
        ('LIST_END',   r'>'),
        # Correctly capture only the inner value for ASCII and UINT
        ('VALUE',      r"<\s*(?:A|U\d)\s*\[\d+\]\s*(?:'([^']*)'|(\d+))\s*>"),
        ('SKIP',       r'[\s\n]+'),
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    
    for mo in re.finditer(tok_regex, text):
        kind = mo.lastgroup
        if kind == 'SKIP':
            continue
        
        value = mo.group(kind)
        if kind == 'VALUE':
            # The regex for VALUE has two groups; one will be None.
            yield 'VALUE', mo.group(2) or mo.group(3)
        else:
            yield kind, value

def build_tree(tokens):
    """Builds a nested Python list from a stream of tokens."""
    stack = [[]]
    for kind, value in tokens:
        if kind == 'LIST_START':
            new_list = []
            stack[-1].append(new_list)
            stack.append(new_list)
        elif kind == 'LIST_END':
            if len(stack) > 1:
                stack.pop()
        elif kind == 'VALUE':
            stack[-1].append(value)
    return stack[0]
