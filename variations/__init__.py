import os

from sphinx.util import status_iterator
from sphinx.util.osutil import os_path
import sphinx.builders.html
import sphinx.directives.other
import sphinx.addnodes
import sphinx.util.build_phase

import docutils.nodes
import docutils.io

__version__ = '1.0.5'

class VariationNode(docutils.nodes.Element):
    """
    Node that is used to differentate from a regular `only` node.
    It inherits from the same class that `only` does, which is also empty,
    so *in theory* changing one of those node's __class__ to this shouldn't
    have any ill effect.
    """


class OnlyVariationDirective(sphinx.directives.other.Only):
    """
    A simple directive that overrides the directive for `only`, but basically
    retains the same functionality.
    """

    def run(self):
        """
        Checks if the tag is in the list of doc variations. If it is, turn it
        into a `VariationNode`
        """
        nodes = super().run()
        if nodes and (self.arguments[0] in [var[0] for var in self.config.variations]):
            nodes[0].__class__ = VariationNode

        return nodes


try:
    from readthedocs_ext.readthedocs import ReadtheDocsBuilder
    builder_base = ReadtheDocsBuilder
except ImportError:
    builder_base = sphinx.builders.html.StandaloneHTMLBuilder

class HTMLVariationBuilder(builder_base):
    """
    Outputs multiple variations of the documentation, with differing variations
    enabled/disabled.
    """

    def __init__(self, app):
        super().__init__(app)

        self.current_variation = self.config.variations[0]

    def get_outfilename(self, pagename):
        """
        Same as super()'s, but adds in the current variation as an
        intermediate directory.
        """
        return os.path.join(self.outdir,
                            self.current_variation[0],
                            os_path(pagename) + self.out_suffix)

    def get_target_uri(self, docname, typ=None):
        """
        Same as super()'s, but adds in the current variation as an
        intermediate directory.
        """
        return self.current_variation[0] + '/' + docname + self.link_suffix

    def _write_serial(self, docnames):
        """
        Loops through each variation, which causes each docname to be
        written multiple times depending on which is active.
        """
        for docname in status_iterator(docnames, 'writing output... ',
                                       "darkgreen", len(docnames),
                                       self.app.verbosity):
            for variation in self.config.variations:
                self.current_variation = variation

                self.app.phase = sphinx.util.build_phase.BuildPhase.RESOLVING
                doctree = self.env.get_and_resolve_doctree(docname, self)
                self.app.phase = sphinx.util.build_phase.BuildPhase.WRITING
                self.write_doc_serialized(docname, doctree)
                self.write_doc(docname, doctree)

    def gen_additional_pages(self):
        """Make sure any other files are written to the correct place as well."""

        for variation in self.config.variations:
            self.current_variation = variation

            for pagelist in self.app.emit('html-collect-pages'):
                for pagename, context, template in pagelist:
                    self.handle_page(pagename, context, template)

            # additional pages from conf.py
            for pagename, template in self.config.html_additional_pages.items():
                self.handle_page(pagename, {}, template)

            # the search page
            if self.search:
                self.handle_page('search', {}, 'search.html')

            # the opensearch xml file
            if self.config.html_use_opensearch and self.search:
                fn = path.join(self.outdir, '_static', 'opensearch.xml')
                self.handle_page('opensearch', {}, 'opensearch.xml',
                                 outfilename=fn)

    def write_genindex(self):
        for variation in self.config.variations:
            self.current_variation = variation
            super().write_genindex()

    def update_page_context(self, pagename, templatename, ctx, event_arg):
        """Give templates information on the current variation."""
        ctx['currentvariation'] = self.current_variation
        ctx['variations'] = self.config.variations

        if self.current_variation and 'theme_canonical_url' in ctx:
            ctx['theme_canonical_url'] += self.current_variation[0] + '/'


def visit_variation_node(self, node):
    """Skip the node if it's not the current variation, otherwise noop."""
    if self.builder.current_variation[0] != node['expr']:
        raise docutils.nodes.SkipNode

def depart_variation_node(self, node):
    pass

def builder_inited(app):
    """
    This is the earliest event hook possible, hopefully adding stuff here
    doesn't screw anything up. We only want our stuff to run when we're using
    the regular old HTML builder.
    """
    if app.builder.name in ['html', 'readthedocs']:
        app.add_node(VariationNode,
                     html=(visit_variation_node, depart_variation_node))
        app.add_directive('only', OnlyVariationDirective, override=True)

def setup(app):
    app.add_config_value('variations', [], 'env')
    app.add_builder(HTMLVariationBuilder, override=True)

    app.connect('builder-inited', builder_inited)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': False,
    }
