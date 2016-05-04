letters = "abcdefghigklmnopqrstuvwxyz"
digits = "0123456789"
single_delimiters = {
    ';': ord(';'),
    '.': ord('.'),
    ',': ord(','),
    ':': ord(':'),
    '=': ord('='),
    '-': ord('-'),
    '$': ord('$'),
    '(': ord('('),
    ')': ord(')'),
    '#': ord('#'),
    '\'': ord('\''),
    '\\': ord('\\'),
}
double_delimiters = {
    ':=': 301,
    '..': 302
}
delimiters = single_delimiters
delimiters.update(double_delimiters)
signs = "+-"
whitespaces = [' ', '\n', '\t', '\r', '\f']
keywords_table = {
    'program': 401,
    'procedure': 402,
    'const': 403,
    'begin': 404,
    'end': 405,
    'var': 406,
    'signal': 407,
    'complex': 408,
    'integer': 409,
    'float': 410,
    'blockfloat': 411,
    'ext': 412,
    'deffunc': 413,
    'link': 414,
    'in': 415,
    'out': 416,
    'exp': 417,
}
