import re

_ruby_block_comment = re.compile(r'(?m)^\s*=begin\b.*?^\s*=end\b', re.DOTALL)
_ruby_line_aware = re.compile(
    r'(?P<sq>\'(?:\\.|[^\\\'])*\')|(?P<dq>"(?:\\.|[^\\"])*")|(?P<c>\#.*?$)',
    re.MULTILINE | re.DOTALL
)

def _strip_ruby_comments(code: str) -> str:
    code = _ruby_block_comment.sub('', code)
    out = []
    last_end = 0
    for m in _ruby_line_aware.finditer(code):
        if m.lastgroup in ('sq', 'dq'):
            out.append(code[last_end:m.end()])
            last_end = m.end()
        else:
            out.append(code[last_end:m.start()])
            last_end = m.end()
    out.append(code[last_end:])
    return ''.join(out)

_erb_comment = re.compile(r'<%#.*?%>', re.DOTALL)
_erb_code = re.compile(r'<%(?!#)(=?|-)?(.*?)-?%>', re.DOTALL)

def _strip_ruby_in_erb(doc: str) -> str:
    doc = _erb_comment.sub('', doc)
    def repl(m):
        prefix = m.group(1) or ''
        inner = m.group(2) or ''
        processed = _strip_ruby_comments(inner)
        return f'<%{prefix}{processed}%>'
    return _erb_code.sub(repl, doc)

def removeComment(string, ext=None):
    ext = (ext or '').lower()
    if ext == 'rb':
        return _strip_ruby_comments(string)
    if ext == 'erb':
        return _strip_ruby_in_erb(string)
    c_regex = re.compile(
        r'(?P<comment>//.*?$|[{}]+)|(?P<multilinecomment>/\*.*?\*/)|(?P<noncomment>\'(\\.|[^\\\'])*\'|"(\\.|[^\\"])*"|.[^/\'"]*)',
        re.DOTALL | re.MULTILINE
    )
    return ''.join([c.group('noncomment') for c in c_regex.finditer(string) if c.group('noncomment')])


code ="""
<html>
  <body>
    <%# 이건 ERB 주석입니다. HTML로 렌더링되지 않습니다. %>
    <h1><%= greet("Ruby") %></h1>

    <% # Ruby 한 줄 주석 (코드 내부) %>
    <% if true %>
      <p>Hello world!</p>
    <% end %>

    <%=
      # ERB 안쪽 Ruby 주석
      add(2, 3)
    %>
  </body>
</html>


"""

print(removeComment(code, "erb"))