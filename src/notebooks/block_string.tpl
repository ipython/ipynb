{%- extends 'python.tpl' -%}

{%- block markdowncell scoped -%}
"""
{{ cell.source}}
"""
{% endblock markdowncell %}