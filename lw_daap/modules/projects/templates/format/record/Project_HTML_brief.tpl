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

{% from "format/record/record_macros.tpl" import render_authors, render_access_rights, render_deposition_type %}
{% from "projects/macros.tpl" import action_buttons with context %}

{% set record = get_updated_record(record) %}

{% block record_row %}
<tr>
  <td>
  <h4 class="record-header">
  {% block record_header -%}
    <a href="{{ url_for('record.metadata', recid=record['recid']) }}">
        {{ record.get('title', '') }}
        <small class="text-muted">{{ record.description|sentences(3) }}</small>
    </a>
  {%- endblock %}
  </h4>
  <p class="record-info">
  {% block record_info %}
    {{ render_access_rights(record) if record.get('access_right') }}  |
    {{ render_deposition_type(record) if record.get('upload_type') }} |
    {% if record.get('doi') %}
        {% set image_url = url_for('lwdaap_pids.doi_badge', doi=record.get('doi'), _external=True, _scheme='https') %}
        <a href="http://dx.doi.org/{{record.get('doi')}}" title="DOI" target="_blank">        
            <span class="get-badge" data-toggle="tooltip" data-placement="bottom" title="Get the DOI badge!">
                <img src="{{image_url}}" alt="{{record.get('doi')}}"/>          
            </span>  
        </a> |
    {% endif %}
        {% set image_url = url_for('lwdaap_pids.pid_badge', pid=get_pid(record.recid), _external=True, _scheme='https') %}
        <a href="{{url_for('record.metadata', recid=record.recid)}}" title="PID" target="_blank">        
            <span class="get-badge" data-toggle="tooltip" data-placement="bottom" title="Get the PID badge!">
                <img src="{{image_url}}" alt="{{get_pid(record.recid)}}"/>          
            </span>  
        </a> |
    {{ record.publication_date }}
  {% endblock %}
  </p>
  </td>
  <td style="vertical-align: middle">
  {% block record_actions %}
    {{ action_buttons(tab, record) }}
  {% endblock %}
  </td>
</tr>
{% endblock %}
