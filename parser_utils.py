# parser_utils.py
import re

def tokenize(text):
    """Breaks the SECS message text into a stream of tokens."""
    spec = [('L_S', r'<\s*L\s*\[\d+\]\s*>'), ('L_E', r'>'), ('A', r"<\s*A\s*\[\d+\]\s*'([^']*)'\s*>"), ('U', r"<\s*U\d\s*\[\d+\]\s*(\d+)\s*>"), ('S', r'[\s\n]+')]
    tok_regex = '|'.join('(?P<%s>%s)' % p for p in spec)
    for mo in re.finditer(tok_regex, text):
        k, v = mo.lastgroup, mo.group()
        if k == 'S': continue
        yield k, v

def build_tree(tokens):
    """Builds a nested Python list from a stream of tokens."""
    stack = [[]]
    for k, v in tokens:
        if k == 'L_S':
            new_list = []; stack[-1].append(new_list); stack.append(new_list)
        elif k == 'L_E':
            if len(stack) > 1: stack.pop()
        else:
            val_match = re.search(r"'([^']*)'|(\d+)", v)
            if val_match: stack[-1].append(val_match.group(1) or val_match.group(2))
    return stack[0]
