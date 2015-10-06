from invenio.utils.forms import InvenioBaseForm
from wtforms import RadioField, SelectField, StringField, validators


class LaunchFormData:
    """
    Helper Class to pass when initializing the LaunchForm
    """
    def _get_value_from_id(self, reqs, id):
        for k, v in reqs.items():
            if v['id'] == id:
                return k
        return None

    def __init__(self, reqs, title=None, flavor=None, os=None, app_env=None, **kwargs):
        if title:
            self.name = title[0]
        if flavor:
            self.flavor = self._get_value_from_id(reqs['flavors'], flavor[0])
        if os:
            self.image = self._get_value_from_id(reqs['images'], os[0])
        if app_env:
            self.app_env = self._get_value_from_id(reqs['app_envs'], app_env[0])


class LaunchForm(InvenioBaseForm):
    name = StringField(
        label = 'Instance Name',
        description= 'Required. A name that helps to identify your instance',
        validators=[validators.DataRequired(),
                    validators.length(
                        max=50,
                        message=("The identifier must be less "
                                 "than 50 characters long.")),
                   ],
    )

    flavor = SelectField(
        label = 'Flavor',
        description = 'Required. Size of the VM to start',
    )

    image = SelectField(
        label = 'Operating System',
        description = 'Required. Operating System to use',
    )

    app_env = SelectField(
        label = 'Application environment',
        description = 'Required. Some info?',
    )

    def _build_choices(self, reqs, req_type, title_field='title'):
        return [(k, v[title_field]) for k, v in reqs.get(req_type, {}).items()]

    def fill_fields_choices(self, reqs):
        self.flavor.choices = self._build_choices(reqs, 'flavors', 'id')
        self.image.choices = self._build_choices(reqs, 'images')
        self.app_env.choices = self._build_choices(reqs, 'app_envs')
