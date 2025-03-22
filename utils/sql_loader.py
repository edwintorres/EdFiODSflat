from jinja2 import Template

def render_sql(path, context):
    """
    Renders a SQL file using Jinja2 with the given context.
    Example: render_sql("sql/my_query.sql", {"table": "students"})
    """
    with open(path) as f:
        template = Template(f.read())
    return template.render(**context)
