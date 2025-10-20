# parser_utils.py
import re
def tokenize(text):
    spec = [('L_S',r'<\s*L\s*\[\d+\]\s*>'),('L_E',r'>'),('A',r"<\s*A\s*\[\d+\]\s*'([^']*)'\s*>"),('U',r"<\s*U\d\s*\[\d+\]\s*(\d+)\s*>"),('S',r'[\s\n]+')]
    regex = '|'.join('(?P<%s>%s)' % p for p in spec)
    tokens = []
    for mo in re.finditer(regex, text):
        k, v = mo.lastgroup, mo.group()
        if k == 'S': continue
        elif k in ['L_S', 'L_E']: tokens.append((k, v))
        else: tokens.append((k, mo.group(1) or mo.group(2)))
    return tokens
def build_tree(tokens):
    stack = [[]]
    for k, v in tokens:
        if k == 'L_S':
            new_list = []; stack[-1].append(new_list); stack.append(new_list)
        elif k == 'L_E':
            if len(stack) > 1: stack.pop()
        else: stack[-1].append(v)
    return stack[0]
