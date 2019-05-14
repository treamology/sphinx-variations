import os

from sphinx.util import status_iterator
from sphinx.util.osutil import os_path
import sphinx.builders.html
import sphinx.directives.other
import sphinx.addnodes
import sphinx.util.build_phase

import docutils.nodes
import docutils.io

class VariationNode(docutils.nodes.Element):
    """Node that is used to differentate from a regular `only` node."""


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
        if self.arguments[0] in self.config.variations and nodes:
            nodes[0].__class__ = VariationNode

        return nodes


class HTMLVariationBuilder(sphinx.builders.html.StandaloneHTMLBuilder):
    """
    Outputs multiple variations of the documentation, with differing variations
    enabled/disabled.
    """

    def get_outfilename(self, pagename):
        """
        Same as super()'s, but adds in the current variation as an
        intermediate directory.
        """
        return os.path.join(self.outdir,
                            self.docwriter.current_variation,
                            os_path(pagename) + self.out_suffix)

    def get_target_uri(self, docname, typ=None):
        """
        Same as super()'s, but adds in the current variation as an
        intermediate directory.
        """
        return os.path.join(self.docwriter.current_variation,
                            docname + self.link_suffix)

    def _write_serial(self, docnames):
        """
        Loops through each variation, which causes each docname to be
        written multiple times depending on which is active.
        """
        for docname in status_iterator(docnames, 'writing output... ',
                                       "darkgreen", len(docnames),
                                       self.app.verbosity):
            for variation in self.config.variations:
                self.docwriter.current_variation = variation

                self.app.phase = sphinx.util.build_phase.BuildPhase.RESOLVING
                doctree = self.env.get_and_resolve_doctree(docname, self)
                self.app.phase = sphinx.util.build_phase.BuildPhase.WRITING
                self.write_doc_serialized(docname, doctree)
                self.write_doc(docname, doctree)

    def gen_additional_pages(self):
        """Make sure any other files are written to the correct place as well."""
        for pagelist in self.app.emit('html-collect-pages'):
            for pagename, context, template in pagelist:
                self.handle_page(pagename, context, template)

        for variation in self.config.variations:
            self.docwriter.current_variation = variation

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


def visit_variation_node(self, node):
    """Skip the node if it's not the current variation, otherwise noop."""
    if self.builder.docwriter.current_variation != node['expr']:
        raise docutils.nodes.SkipNode

def depart_variation_node(self, node):
    pass

def setup(app):
    app.add_config_value('variations', [], 'env')

    app.add_builder(HTMLVariationBuilder, override=True)
    app.add_node(VariationNode,
                 html=(visit_variation_node, depart_variation_node))
    app.add_directive('only', OnlyVariationDirective, override=True)

    return {
        'version': '0.1',
        'parallel_read_safe': True,
        'parallel_write_safe': False,
    }
