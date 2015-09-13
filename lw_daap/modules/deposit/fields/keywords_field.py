from lw_daap.modules.invenio_deposit.fields import TextAreaField


__all__ = ['KeywordsField']


class KeywordsField(TextAreaField):
    def process_data(self, value):
        if not  isinstance(value, (list, tuple)):
           value = (value, )
        self.data = (', ').join(value)
