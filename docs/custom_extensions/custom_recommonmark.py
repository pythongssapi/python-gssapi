from recommonmark.parser import CommonMarkParser
from docutils import nodes

# treats "verbatim" (code without a language specified) as a code sample
class AllCodeCommonMarkParser(CommonMarkParser):
    def verbatim(self, text):
        node = nodes.literal_block(text, text)
        self.current_node.append(node)
