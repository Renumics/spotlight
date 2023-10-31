## docusaurus compatible variant of the default pdoc markdown template

<%
  import re
  import pdoc
  from pdoc.html_helpers import to_markdown as _to_markdown

  def to_markdown(text):
    ## wrapper around pdoc's to_markdown helper
    ## with some additional cleanup steps needed for docusaurus

    text = _to_markdown(text, module=module)

    ## pdoc outputs a quirky variant for inner headings:
    ##   Title
    ##   -----=
    ## replace them with a simple h4:
    ##   #### Title
    text = re.sub(r'([^\n]+)\n-+=', r'#### \g<1>\n', text)

    ## A ton of the current examples is in python repl form
    ## and declares `python-repl` as the language
    ## of the corresponding code blocks
    ## replace this with `python` for prismjs
    text = text.replace("```python-repl", "```python")

    return text
%>

## A bunch of helper methods to simplify the main output logic

<%def name="h3(s)">### ${s}
</%def>
<%def name="h4(s)">#### ${s}
</%def>

<%def name="function(func)" buffered="True">
${h3(f"`{func.name}({', '.join(func.params(annotate=False))})` {{#{func.qualname}()}}")}
${func.docstring | to_markdown }
</%def>

<%def name="method(func)" buffered="True">
${h4(f"`{func.name}({', '.join(func.params(annotate=False))})` {{#{func.qualname}()}}")}
${func.docstring | to_markdown }
</%def>

<%def name="variable(var)" buffered="True">
`${var.name}`
${var.docstring | to_markdown}
</%def>

<%def name="class_(cls)" buffered="True">
${h3(f"`{cls.name}({', '.join(cls.params(annotate=False))})` {{#{cls.qualname}}}")}
${cls.docstring | to_markdown}
<%
  class_vars = cls.class_variables(show_inherited_members, sort=sort_identifiers)
  static_methods = cls.functions(show_inherited_members, sort=sort_identifiers)
  inst_vars = cls.instance_variables(show_inherited_members, sort=sort_identifiers)
  methods = cls.methods(show_inherited_members, sort=sort_identifiers)
  mro = cls.mro()
  subclasses = cls.subclasses()
%>

% if static_methods:
${h4('Static methods')}
% for f in static_methods:
${method(f)}
% endfor
% endif

% if inst_vars:
${h4('Instance variables')}
% for v in inst_vars:
${variable(v)}
% endfor
% endif

% if methods:
${h4('Methods')}
% for m in methods:
${method(m)}
% endfor
% endif
</%def>

## Start the output logic for an entire module.

<%
  variables = module.variables(sort=False)
  classes = module.classes(sort=False)
  functions = module.functions(sort=False)
  submodules = module.submodules()
  heading = 'Namespace' if module.is_namespace else 'Module'
  shortname = module.name.split('.')[-1]
%>

---
id: ${shortname}
title: ${shortname}
---

${module.docstring}

% if variables:
Variables
---------
% for v in variables:
${variable(v)}

% endfor
% endif

% if functions:
Functions
---------
% for f in functions:
${function(f)}

% endfor
% endif

% if classes:
Classes
-------
% for c in classes:
${class_(c)}

% endfor
% endif
