#
# add hbpro format
#

from invenio.modules.search import fixtures as defaults

class FormatData(defaults.FormatData):
    class FormatHBPro:
        code = u'hbpro'
        last_updated = None
        description = u'HTML brief output format provisional, used for curation.'
        content_type = u'text/html'
        visibility = 1
        name = u'HTML brief Provisional'
