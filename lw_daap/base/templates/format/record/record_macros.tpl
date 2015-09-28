#
# (c) 2015 aeonium. 
#

{# TODO: use the max parameter #}
{%- macro render_authors(record, max=None) %}
{% if record.authors %}
{% for author in record.authors %}
<a href="{{ url_for('search.search', p='author:"' + author.name + '"') }}">
  {{ author.name }}
</a>
<a href="{{ url_for('search.search', p='affiliation:"' + author.affiliation + '"') }}">
  {{ ' (<span class="text-muted">' ~ author.affiliation ~ '</span>)' if author.affiliation }}
</a>
{% if not loop.last %};
{% endif %}
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

{%- macro render_deposition_type(record, max=None) %}
{% set label_types = {
'software': 'label-success',
'dataset': 'label-danger',
'analysis': 'label-warning',
}
%}
{% if record.upload_type %}
<span class="label {{ label_types[record.upload_type] }}">{{ record.upload_type }}</span>
{% endif %}
{% endmacro -%}


{%- macro open_panel_section (heading, key, collapse=False) %}
<div class="panel panel-deposit panel-sharp">
  <div class="panel-heading">
    <a data-toggle="collapse" class="panel-toggle" href="#collapse-{{key}}">
      {{ heading }}
      <span class="pull-right show-on-collapsed">
        <i class="fa fa-chevron-down"></i>
      </span>
      <span class="pull-right hide-on-collapsed">
        <i class="fa fa-chevron-up"></i>
      </span>
    </a>
  </div>
  <div id="collapse-{{key}}" class="panel-collapse collapse {%if not collapse %}in{%endif %}">
    <div class="panel-body">
{% endmacro -%}

{%- macro close_panel_section() %}
</div></div></div>
{% endmacro -%}

