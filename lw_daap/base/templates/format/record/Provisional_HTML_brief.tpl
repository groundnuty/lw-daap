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

{#
# This file is part of Invenio.
# Copyright (C) 2014 CERN.
#
# Invenio is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# Invenio is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Invenio; if not, write to the Free Software Foundation, Inc.,
# 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
#}

{% from "communities/helpers.html" import curation_buttons with context %}
{% from "format/record/record_macros.tpl" import render_authors, render_access_rights %}

{% bundle "communities.js" %}

{% macro render_record_footer(number_of_displayed_authors) %}
    <p>
      {{ render_authors(record, 4) if record.get('authors') }}
      |
      <i class="fa fa-calendar"></i> {{ record.get('creation_date')|invenio_format_date() }}
      |
      {% if record.doi %}
      <a href="http://dx.doi.org/{{ record.doi }}s" title="DOI" target="_blank"><i class="fa fa-barcode"></i> {{ record.doi }}</a>
      |
      {% endif %}
      {{ render_access_rights(record) if record.get('access_right') }}

      {% if record['keywords']|length %} | <i class="fa fa-tags"></i>
      |
      {% for keyword in record['keywords'] %}
      <span class="label label-default" style="display: inline-block; margin: 5px, 5px;">
        <a href="{{ url_for('search.search', p='keyword:' + keyword) }}">
          {{ keyword }}
        </a>
      </span>
      &nbsp
      {% endfor %}
      {% endif %}
    </p>
{% endmacro %}

{% block record_brief %}
<div class="htmlbrief">
    {% block record_header %}
    <h4 class="media-heading">
        <a href="{{ url_for('record.metadata', recid=record['recid']) }}">
            {{ record.get('title', '') }}</a>
    </h4>
    {% endblock %}
    {% block record_content %}
    <div>
        <p class="record-abstract">
          {{ record.get('description', '')|sentences(3) }}
        </p>
    </div>
    {% endblock %}

    <div class="clearfix"></div>
    <div class="row">
        <div class="col-md-6">
            {% block record_footer %}
                {{ render_record_footer(4) }}
            {% endblock %}
        </div>
        <div class="col-md-6">
            {%- set comm_id = collection|community_id %}
            {{ curation_buttons(bfo, comm_id) }}
        </div>
    </div>
</div>
{% endblock %}
