#
#

from fixture import DataSet


class CommunityData(DataSet):
    class daap:
        id = 'daap'
        title = 'LifeWatch Data Access and Preservation'
        id_user = 1

    class cuerda_del_pozo:
        id = 'cuerdadelpozo'
        title = 'Cuerda del Pozo',
        curation_policy = ('Datasets related to the Cuerda del Pozo ' 
                           'reservoir at Soria')
        id_user = 1 
