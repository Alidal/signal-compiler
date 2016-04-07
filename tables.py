letters = "abcdefghigklmnopqrstuvwxyz"
digits = "0123456789"
signs = "+-"
delimiters = [';', ':=', '.', ',', '=', '-', '..', '\\', '#']
whitespaces = [' ', '\n', '\t', '\r', '\f']
keywords_table = [
    'program', 'procedure', 'const', 'begin', 'end', 'var', 'signal',
    'complex', 'integer', 'float', 'blockfloat', 'ext', 'deffunc', 'link', 'in',
    'out', '$exp'
]

dm_table = {
    ';': 59,
    '.': 46,
    ',': 44,
    '=': 61,
    ':=': 301
}

error_table = {'identifier/number error': -1,
               'unknown symbol': -2,
               'comment error': -3}
