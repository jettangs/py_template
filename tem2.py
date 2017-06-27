#coding=utf-8
import re

class CodeBuilder:
    INDENT_STEP = 4     # 每次缩进的空格数

    def __init__(self, indent=0):
        self.indent = indent    # 当前缩进
        self.lines = []         # 保存一行一行生成的代码

    def forward(self):
        """缩进前进一步"""
        self.indent += self.INDENT_STEP

    def backward(self):
        """缩进后退一步"""
        self.indent -= self.INDENT_STEP

    def add(self, code):
        self.lines.append(code)

    def add_line(self, code):
        self.lines.append(' ' * self.indent + code)

    def __str__(self):
        """拼接所有代码行后的源码"""
        return '\n'.join(map(str, self.lines))

    def __repr__(self):
        """方便调试"""
        return str(self)


class Template:

    def __init__(self, raw_text, indent=0, default_context=None,
                 func_name='__func_name', result_var='__result'):
        self.raw_text = raw_text
        self.default_context = default_context or {}
        self.func_name = func_name
        self.result_var = result_var
        self.code_builder = code_builder = CodeBuilder(indent=indent)
        self.buffered = []
        # 变量
        self.re_variable = re.compile(r'\{\{ .*? \}\}')
        # 注释
        self.re_comment = re.compile(r'\{# .*? #\}')
        # 标签
        self.re_tag = re.compile(r'\{% .*? %\}')
        # 用于按变量，注释，标签分割模版字符串
        self.re_tokens = re.compile(r'((?:\{\{ .*? \}\})|(?:\{\# .*? \#\})|(?:\{% .*? %\}))')

        # 生成 def __func_name():
        code_builder.add_line('def {}():'.format(self.func_name))
        code_builder.forward()
        # 生成 __result = []
        code_builder.add_line('{} = []'.format(self.result_var))
        
        # 解析模版
        self._parse_text()
        self.flush_buffer()
        # 生成 return "".join(__result)
        code_builder.add_line('return "".join({})'.format(self.result_var))
        code_builder.backward()

    def _parse_text(self):
        
        tokens = self.re_tokens.split(self.raw_text)
        
        for token in tokens:
            # {{ variable }}
            if self.re_variable.match(token):
                variable = token.strip('{} ') #移除首尾的{}和空格
                self.buffered.append('str({})'.format(variable))
            # {# variable #}
            elif self.re_comment.match(token):
                continue
            # {% tag %}
            elif self.re_tag.match(token):
                # 将前面解析的字符串，变量写入到 code_builder 中
                # 因为标签生成的代码需要新起一行
                self.flush_buffer()
                tag = token.strip('{%} ')
                tag_name = tag.split()[0] #默认空格隔开 ['for', 'skill', 'in', 'skills']
                if tag_name in ('if', 'elif', 'else', 'for'):
                    # elif 和 else 之前需要向后缩进一步
                    if tag_name in ('elif', 'else'):
                        self.code_builder.backward()
                    self.code_builder.add_line('{}:'.format(tag))
                    # if/for 表达式部分结束，向前缩进一步，为下一行做准备
                    self.code_builder.forward()
                elif tag_name in ('endif', 'endfor'):
                    # if/for 结束，向后缩进一步
                    self.code_builder.backward()
            # 普通字符串
            else:
                self.buffered.append('{}'.format(repr(token)))

    def flush_buffer(self):
        # 生成类似代码: __result.extend(['<h1>', name, '</h1>'])
        print self.buffered
        line = '{0}.extend([{1}])'.format(
            self.result_var, ','.join(self.buffered)
        )
        self.code_builder.add_line(line)
        self.buffered = []

    def render(self, context=None):
        print self.buffered
        print "------------"
        print str(self.code_builder)
        """渲染模版"""
        namespace = {}
        namespace.update(self.default_context)
        if context:
            namespace.update(context)
        exec(str(self.code_builder), namespace)
        result = namespace[self.func_name]()
        return result
		

studentT = '''
<h1>hello, {{ name }}</h1>
{% for skill in skills %}
    <p>you are good at {{ skill }}.</p>
    {% for key in keys %}
        <p>{{key}}</p>
    {% endfor %}
{% endfor %}
'''

student = {'name': 'Eric', 'skills': ['python', 'english', 'music', 'comic'],'keys':['A','B','C']}

print Template(studentT).render(student)

#print Template('{{ 1 + 2 }}').render()

personT = '''
<div>
    <p>welcome, {{ person['name'] }}</p>
    <ul>
        {% for item, value in person['info'].items() %}
        <li>{{ item }}: {{ value }}</li>
        {% endfor %}
    </ul>
</div>
'''

person = {"name":"kcetry", "info":{"age":"18","sex":"female"}}

#print Template(personT).render({'person': person})
