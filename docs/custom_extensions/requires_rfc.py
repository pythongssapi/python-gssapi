import sys

from docutils import nodes
from docutils.parsers.rst import roles


def setup(app):
    app.add_role('requires-ext', RequiresExtRole(app))


class RequiresExtRole(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, name, rawtext, text, lineno, inliner,
                 options={}, content=[]):
        if text.startswith('rfc'):
            rfc_text = text[3:]

            rfc_node, rfc_msg = roles.rfc_reference_role(
                'rfc', ':rfc:`%s`' % rfc_text, rfc_text, lineno,
                inliner, options, content)

            if rfc_msg:
                # error
                return (rfc_node, rfc_msg)
            else:
                middle_parts = rfc_node + [nodes.Text(" extension",
                                                      " extension")]
        else:
            ext_name = 'gssapi.raw.ext_%s' % text
            # autodoc has already imported everything
            try:
                ext_module = sys.modules[ext_name]
            except KeyError:
                ext_title = text + " extension"
            else:
                if ext_module.__doc__:
                    ext_title = ext_module.__doc__.splitlines()[0]
                else:
                    ext_title = text + " extension"
            ref_nodes, ref_messages = self.app.env.domains['py'].role('mod')(
                'mod', rawtext, ext_name, lineno, inliner)

            if ref_messages:
                # error
                return (ref_nodes, ref_messages)

            title_node = nodes.Text(ext_title, ext_title)

            ref_nodes[0].clear()
            ref_nodes[0].append(title_node)

            middle_parts = ref_nodes

        begin_text = nodes.Text("requires the ", "requires the ")

        main_nodes = [begin_text] + middle_parts
        wrapper_node = nodes.emphasis('', '', *main_nodes)

        return ([nodes.Text('', ''), wrapper_node, nodes.Text('', '')], [])
