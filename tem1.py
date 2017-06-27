HTML = '''
<div>
    <p>welcome, {name}</p>
    <ul>
        {info}
    </ul>
</div>
'''

person = {"name" : "kcetry", "info" :{"age":"18","sex":"female"}}

def gen_html(person):
    name = person['name']
    info_list = [
        '<li>{0}: {1}</li>'.format(item, value)
        for item, value in person['info'].items()
    ]
    info = '\n'.join(info_list)
    return HTML.format(name=name, info=info)
	
print gen_html(person)