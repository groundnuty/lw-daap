#
#

from fixture import DataSet
from invenio.modules.search import fixtures as default

siteCollection = default.CollectionData.siteCollection

class CollectionData(DataSet):
    class analysis(object):
        id = 2
        name = 'Analysis'
        dbquery = '980__a:analysis'

    class dataset(object):
        id = 3
        name = 'Dataset'
        dbquery = '980__a:dataset'

    class software(object):
        id = 4
        name = 'Software'
        dbquery = '980__a:software'

    class communities(object):
        id = 5
        name = 'communities-collection'
        dbquery = None


class CollectionCollectionData(DataSet):
    class site_analysis:
        dad = siteCollection
        son = CollectionData.analysis
        score = 0
        type = 'r'

    class site_dataset:
        dad = siteCollection
        son = CollectionData.dataset
        score = 0
        type = 'r'

    class site_software:
        dad = siteCollection
        son = CollectionData.software
        score = 0
        type = 'r'
