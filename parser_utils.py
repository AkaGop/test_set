# parser_utils.py
import re

def tokenize(text):
    """Breaks the SECS message text into a stream of tokens."""
    token_specification = [
        ('LIST_START', r'<\s*L\s*\[\d+\]\s*>'),
        ('LIST_END',   r'>'),
        ('ASCII',      r"<\s*A\s*\[\d+\]\s*'([^']*)'\s*>"),
        ('UINT',       r"<\s*U\d\s*\[\d+\]\s*(\d+)\s*>"),
        ('SKIP',       r'[\s\n]+'), # Skip whitespace and newlines
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    tokens = []
    for mo in re.finditer(tok_regex, text):
        kind = mo.lastgroup
        value = mo.group(kind)
        if kind == 'SKIP':
            continue
        elif kind == 'LIST_END':
            tokens.append(('LIST_END', '>'))
        elif kind == 'LIST_START':
            tokens.append(('LIST_START', value))
        else: # ASCII or UINT
            # The regex for ASCII and UINT has one capturing group
            tokens.append((kind, value.strip()))
    return tokens

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
        else: # ASCII or UINT
            # Extract the actual value using regex from the full tag
            val_match = re.search(r"'([^']*)'|(\d+)", value)
            if val_match:
                # Add the string or the number, whichever was found
                stack[-1].append(val_match.group(1) or val_match.group(2))
    return stack[0]
