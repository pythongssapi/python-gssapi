from docutils import nodes
from sphinx.util.nodes import make_refnode

MATCH_RE_RAW = r'\b(([A-Z][A-Za-z0-9]+)+)\b'


def setup(app):
    app.connect('missing-reference', _missing_ref)


def _missing_ref(app, env, node, contnode):
    # skip non-elements
    if not isinstance(contnode, nodes.Element):
        return

    if node.get('refdomain') != 'py':
        return

    options = env.domains['py'].find_obj(
        env, None, None, node.get('reftarget'), node.get('reftype'), 1)

    if not options:
        return

    is_raw = node.get('py:module').startswith('gssapi.raw')

    if len(options) > 1:
        raw_opts = []
        non_raw_opts = []
        for opt in options:
            full_name, type_info = opt
            lib_name, mod_name, _mod_type = type_info
            if mod_name.startswith('gssapi.raw'):
                raw_opts.append(opt)
            else:
                non_raw_opts.append(opt)

        if is_raw:
            if raw_opts:
                choice = raw_opts[0]
            elif non_raw_opts:
                choice = non_raw_opts[0]
            else:
                return
        else:
            if non_raw_opts:
                choice = non_raw_opts[0]
            elif raw_opts:
                choice = raw_opts[0]
            else:
                return
    else:
        choice = options[0]

    choice_name, choice_info = choice
    gssapi, choice_mod, choice_type = choice_info

    if choice_type == 'module':
        return env.domains['py']._make_module_refnode(
            app.builder, node.get('refdoc'), choice_name, contnode)
    else:
        return make_refnode(app.builder, node.get('refdoc'), choice_mod,
                            choice_name, contnode, choice_name)
