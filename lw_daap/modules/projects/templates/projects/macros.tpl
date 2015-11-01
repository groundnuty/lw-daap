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


{% macro curate_buttons(rec) -%} 
  {% if not rec.record_curated_in_project %}
    <a data-toggle="modal" data-target="#curatemodal"
      data-curate-url="{{ url_for('lwdaap_projects.curation', project_id=project.id, record_id=rec.recid) }}" class="btn btn-danger pull-right rmlink" 
      rel="tooltip" title="Curate record"><i class="fa fa-check"></i> Curate</a>
  {% else %} 
    <a data-toggle="modal" data-target="#curatemodal"
      data-curate-url="{{ url_for('lwdaap_projects.curation', project_id=project.id, record_id=rec.recid) }}" class="disabled btn btn-primary pull-right rmlink" 
      rel="tooltip" title="Curate record"><i class="fa fa-check"></i> Curated</a>
  {% endif %}
{%- endmacro %}


{% macro integrate_buttons(rec) -%} 
   <a class="btn btn-md pull-right integrate-chooser {{ 'btn-info' if rec.recid in selected_records else 'btn-danger' }}"
      href="#" data-record-id="{{ rec.recid }}" data-selected="{{ 'true' if rec.recid in selected_records else 'false' }}">
    {{ '<i class="fa fa-check"></i> Unselect' if rec.recid in selected_records else 'Select' }}
  </a>
{%- endmacro %}


{% macro analyze_buttons(rec) -%} 
<a class="btn btn-md btn-danger pull-right" href="{{ url_for('analyze.launch', title=rec.title, flavor=rec.flavor, os=rec.os, app_env=rec.app_env, recid=rec.recid) }}"><i class="fa fa-play-circle-o"></i> Run</a>
{%- endmacro %}


{% macro preserve_buttons(rec) -%} 
  {% if not rec.doi %}
    <a data-toggle="modal" data-target="#doimodal"
      data-doi-url="{{ url_for('lwdaap_projects.preserve', project_id=project.id, record_id=rec.recid) }}" class="btn btn-danger pull-right rmlink" 
      rel="tooltip" title="Publish record"><i class="fa fa-barcode"></i> Mint DOI</a>
  {% else %} 
    <a data-toggle="modal" data-target="#doimodal"
      data-doi-url="{{ url_for('lwdaap_projects.preserve', project_id=project.id, record_id=rec.recid) }}" class="disabled btn btn-primary pull-right rmlink" 
      rel="tooltip" title="Publish record"><i class="fa fa-barcode"></i> Has a DOI</a>
  {% endif %}
{%- endmacro %}


{% macro publish_buttons(rec) -%} 
  {% if not rec.record_public_from_project %}
    <a data-toggle="modal" data-target="#publishmodal"
      data-publish-url="{{ url_for('lwdaap_projects.publication', project_id=project.id, record_id=rec.recid) }}" class="btn btn-danger pull-right rmlink" 
      rel="tooltip" title="Publish record"><i class="fa fa-share"></i> Publish</a>
  {% else %} 
    <a data-toggle="modal" data-target="#publishmodal"
      data-publish-url="{{ url_for('lwdaap_projects.publication', project_id=project.id, record_id=rec.recid) }}" class="disabled btn btn-primary pull-right rmlink" 
      rel="tooltip" title="Publish record"><i class="fa fa-share"></i> Public</a>
  {% endif %}
{%- endmacro %}


{% macro action_buttons(tab, rec) -%}
  {% if tab == "curate" %}
    {{ curate_buttons(record) }}
  {% elif tab == "integrate" %}
    {{ integrate_buttons(record) }}
  {% elif tab == "analyze" %}
    {{ analyze_buttons(record) }}
  {% elif tab == "preserve" %}
    {{ preserve_buttons(record) }}
  {% elif tab == "publish" %}
    {{ publish_buttons(record) }}
  {% endif %}
{%- endmacro %}


{% macro record_table(tab, record_set, title) %}
{%- from "paginate.html" import paginate with context -%}
{%- from "paginate.html" import list_status with context -%}
{% if record_set.items %}
  <table class="table table-hover">
    <thead>
      <tr>
        <th class="col-md-10">{{ title }}</th>
      </tr>
    </thead>
    <tbody>
    {% for rec in record_set.items%}
    <tr>
      {{ format_record(rec.id, of='hbprj', ln=g.ln, tab=tab, project=project, **kwargs)|safe }}
    </tr>
    {% endfor %}
    </tbody>
    {% if record_set.total > per_page %}
    <tfoot>
      <tr>
        <td class="text-center" colspan="2">
          {{ list_status(record_set, page) }}
          {{ paginate(record_set, 'page', small=True) if record_set.items|length }}
        </td>
      </tr>
    </tfoot>
    {% endif %}
  </table>
{% endif %}
{% endmacro %}

