#
# (c) 2015 aeonium. 
#

{# TODO: use the max parameter #}
{%- macro render_authors(record, max=None) %}
{% if record.authors %}
  {% for author in record.authors %}
    <a href="{{ url_for('search.search', p='author:"' + author.name + '"') }}">{{ author.name }}{{ ' (' ~ author.affiliation ~ ')' if author.affiliation }}</a>{% if not loop.last %}; {% endif %}
  {% endfor %}
{% endif %}
{% endmacro -%}

{%- macro render_access_rights(record, max=None) %}
{% set label_types = {'open': 'label-success',
                      'closed': 'label-danger', 
                      'restricted': 'label-warning', 
                      'embargoed': 'label-info', 
                      }
%}
{% if record.access_right %}
  <span class="label {{ label_types[record.access_right] }}">{{ record.access_right }}</span>
  {%- if record.access_right is equalto 'embargoed' -%}, 
     will be available as <span class="label {{ label_types['open'] }}">open access</span> on {{ record.embargo_date }}
  {% endif %}
{% endif %}
{% endmacro -%}


