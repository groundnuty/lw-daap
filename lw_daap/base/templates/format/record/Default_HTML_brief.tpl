{# FIXME: this is just to avoid the "title.title" error, but needs to be completely redone #}


{% extends "format/record/Default_HTML_brief_base.tpl" %}

{% block above_record_header %}{% endblock %}

{% block record_header %}
<a href="{{ url_for('record.metadata', recid=record['recid']) }}">
    {{ record.get('title', '') }}</a>
{% endblock %}

{% block record_content %}
  {{ record.get('description', '')|sentences(3) }}
{% endblock %}

{% block record_info %}
  {#{{ record_info() }} #}
  {{ '<a href="http://dx.doi.org/%(doi)s" title="DOI" target="_blank"><i class="glyphicon glyphicon-barcode"></i> %(doi)s</a>'|format(doi=record['doi']) if record.get('doi') }}
{% endblock %}

{% block fulltext_snippets %}{% endblock %}

{% block record_footer %}{% endblock %}
