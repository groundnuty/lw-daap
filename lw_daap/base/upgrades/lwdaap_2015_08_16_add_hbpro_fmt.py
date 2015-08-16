# taken from Zenodo


from invenio.legacy.dbquery import run_sql

depends_on = []

def info():
    return "Insert hbpro output format"


def do_upgrade():
    """ Implement your upgrades here  """
    res = run_sql("SELECT id FROM format WHERE code='hbpro'")
    if res:
        run_sql("UPDATE format SET code='hbpro', content_type='text/html', "
                "name='HTML brief provisional', visibility=0, "
                "description='HTML brief provisional output format.' "
                "WHERE code='hbpro'")
    else:
        run_sql("INSERT INTO format "
                "(content_type, name, visibility, description, code) "
                "VALUES ('text/html', 'HTML brief provisional', 0, "
                "        'HTML brief provisional output format.', 'hbpro')")
