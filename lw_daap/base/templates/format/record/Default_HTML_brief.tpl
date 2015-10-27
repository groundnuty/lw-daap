{#
 # This file is part of Lifewatch DAAP.
 # Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
 #
 # Lifewatch DAAP is free software; you can redistribute it and/or modify
 # it under the terms of the GNU General Public License as published by
 # the Free Software Foundation, either version 3 of the License, or
 # (at your option) any later version.
 #
 # Lifewatch DAAP is distributed in the hope that it will be useful,
 # but WITHOUT ANY WARRANTY; without even the implied warranty of
 # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 # GNU General Public License for more details.
 #
 # You should have received a copy of the GNU General Public License
 # along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.
 #}

{% from "format/record/record_macros.tpl" import render_authors, render_access_rights %}

{% extends "format/record/Default_HTML_brief_base.tpl" %}

{% block above_record_header %}
{% endblock %}

{% block record_header %}
<a href="{{ url_for('record.metadata', recid=record['recid']) }}">
  {{ record.get('title', '') }}
  <small class="text-muted">{{ record.description|sentences(3) }}</small>
</a>
{% endblock %}

{% block record_content %}
{% endblock %}

{% block record_info %}
  {{ render_access_rights(record) if record.get('access_right') }}  |
  {{ '<span class="label label-primary" style="background: #999">Project</span> |' if record.project_collection }} 
  {{ '<a href="http://dx.doi.org/%(doi)s" title="DOI" target="_blank"><i class="glyphicon glyphicon-barcode"></i> %(doi)s</a> | '|format(doi=record['doi']) if record.get('doi') }} 
  {{ record.publication_date }}

{% endblock %}

{% block fulltext_snippets %}{% endblock %}

{% block record_footer %}{% endblock %}
