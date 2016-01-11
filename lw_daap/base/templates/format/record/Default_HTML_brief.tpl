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

{% from "format/record/record_macros.tpl" import render_authors, render_access_rights, render_deposition_type, label %}

{% extends "format/record/Default_HTML_brief_base.tpl" %}

{% set record = get_updated_record(record) %}

{% block above_record_header %}{% endblock %}

{% block record_header %}
<a href="{{ url_for('record.metadata', recid=record['recid']) }}">
  {{ record.get('title', '') }}
</a>
{% endblock %}

{% block record_content %}
  <small class="text-muted">{{ record.description|sentences(3) }}</small>

    <a href="{{url_for('record.metadata', recid=record.recid)}}" title="PID" target="_blank">
        {{ label('PID', get_pid(record.recid), cbgc='#D9634C') }}
    </a> 
    {% if record.get('doi') %}
    <a href="http://dx.doi.org/{{record.get('doi')}}" title="DOI" target="_blank">
       | {{ label('DOI', record.get('doi'), cbgc='#0F81C2') }}
    </a> 
    {% endif %}
  | {{ render_access_rights(record) if record.get('access_right') }}  
  | {{ render_deposition_type(record) if record.get('upload_type') }} 
  {% if record.record_selected_for_archive %}                                  
        | {{ label(content='archived') }}                                       
  {% endif %} 
  | {{ record.publication_date }}

{% endblock %}

{% block fulltext_snippets %}{% endblock %}

{% block record_footer %}{% endblock %}
