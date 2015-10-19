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

{% block javascript %}
<script type="text/javascript"
src="https://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS-MML_HTMLorMML">
</script>
{% endblock %}

{% from "format/record/record_macros.tpl" import render_authors,
render_access_rights,
render_deposition_type,
render_rel_input,
open_panel_section,
close_panel_section
with context
%}

{% include "lw_daap/pids/doi_modal.html" %}

{% if not daap_record %}
{% set daap_record = record %}
{% endif %}
<div class="record-details">
  {% block header %}
  <div class="row">
    <div class="col-sm-12 col-md-4 pull-right">
    </div>

    <div class="col-sm-12 col-md-8">
      <h2>{{ daap_record.title }}</h2>
    </div>
    <div class="col-sm-12">
      <h4 style="margin-top: 0px">{{ render_authors(daap_record, 4) }}</h4>
    </div>
  </div>

  <div class="spacer30"></div>

  <div class="row">
    {% if summary_view %}
    <div class="col-sm-12 col-md-3">

      {% if current_user.get_id() == daap_record.get('owner', {}).get('id', -1)|int %}     {% if not daap_record.doi and not bfe_is_doi_being_minted(bfo, recid=recid) %}
      <button class="btn btn-block btn-lg btn-default" 
        data-toggle="modal" data-target="#doi-confirm-dialog">
        <i class="fa fa-barcode"></i> Mint Doi</button>
      {% endif %}
      <a class="btn btn-block btn-lg btn-primary" href="{{ url_for('webdeposit.edit', uuid=daap_record.owner.deposition_id|int) }}"><i class="fa fa-pencil-square-o"></i> Edit</a>
      {% endif %}
      {% if daap_record.upload_type != "dataset" %}
      <a class="btn btn-block btn-lg btn-danger" href="{{ url_for('analyze.launch', title=daap_record.title, flavor=daap_record.flavor, os=daap_record.os, app_env=daap_record.app_env) }}"><i class="fa fa-play-circle-o"></i> Run</a>
      {% endif %}
      <div class="spacer20"></div>

      <div class="panel-primary ">
        <div class="panel-heading">
          <i class="fa fa-book"></i> Summary
        </div>
        <div class="panel-body">
          <h4>Publication  Date</h4>{{ daap_record.publication_date }}
          <h4>Persistent Identifier</h4>{% include "lw_daap/pids/doi_info.html" %}
          <h4>Access</h4><h4> {{ render_access_rights(daap_record) }}</h4>
          <h4>Record type</h4><h4> {{ render_deposition_type(daap_record) }}</h4>
          {% if daap_files %}
          <h4>Files</h4>
          {{ daap_files|length }}
          (<span class="text-muted">{{ bfe_daap_filesize(bfo, files=daap_files) | filesizeformat }}</span>)
          {% endif %}
        </div>
      </div>
    </div>
    {% endif %}

    <div class="col-sm-12 col-md-9">
      <div class="panel-list-wrapper">
        <div class="panel panel-default">
          <div class="panel-heading">
            <h3 class="uppercase"><i class="fa fa-thumb-tack"></i> {{ daap_record.upload_type }}</h3>
          </div>
        </div>
        {{ open_panel_section(
        '<i class="fa fa-info"></i> Basic information', 1, False) }}
        <table class="table table-hover">
          <tr>
            <th class="col-md-3"><i class="fa fa-barcode fa-fw"></i> Persistent Identifier</th>
            <td class="col-md-9">{% include "lw_daap/pids/doi_info.html" %}</td>
          </tr>

          {% if daap_record.publication_date %}
          <tr>
            <th class="col-md-3"> <i class="fa fa-calendar fa-fw"></i> Publication Date</th>
            <td class="col-md-9">{{ daap_record.publication_date }}</td>
          </tr>
          {% endif %}

          {% if daap_record.access_right %}
          <tr>
            <th class="col-md-3"><i class="fa fa-pencil fa-fw"></i> Access Rights</th>
            <td class="col-md-9">{{ render_access_rights(daap_record) }}</td>
          </tr>
          {% endif %}

          {% if daap_record.description %}
          <tr>
            <th class="col-md-3"><i class="fa fa-pencil fa-fw"></i> Description</th>
            <td class="col-md-9">{{ daap_record.description }}</td>
          </tr>
          {% endif %}

          {% if daap_record.keywords %}
          <tr>
            <th class="col-md-3"><i class="fa fa-tags fa-fw"></i> Keywords</th>
            <td class="col-md-9">
              {% for keyword in daap_record['keywords'] %}
              <span class="label label-primary" style="display: inline-block; margin: 5px 5px;">
                <a href="{{ url_for('search.search', p='keyword:' + keyword) }}">{{ keyword }}</a>
              </span>
              {% endfor %}
            </td>
          </tr>
          {% endif %}

          {% if daap_record.notes %}
          <tr>
            <th class="col-md-3"><i class="fa fa-pencil fa-fw"></i> Additional Notes</th>
            <td class="col-md-9">{{ daap_record.notes }}</td>
          </tr>
          {% endif %}
        </table>
        {{ close_panel_section() }}


        {% if daap_record.upload_type == "analysis" %}
        {% if daap_record.rel_dataset or daap_record.rel_software %}
        {{ open_panel_section(
        '<i class="fa fa-asterisk"></i> Inputs', 'inputs', True) }}
        <table class="table table-hover">
          <tr>
            <th class="col-md-3"><i class="fa fa-fw fa-laptop"></i> Input dataset</th>
            <td class="col-md-9">{{ render_rel_input(daap_record.rel_dataset) }}</td>
          </tr>
          <tr>
            <th class="col-md-3"><i class="fa fa-fw fa-laptop"></i> Input software</th>
            <td class="col-md-9">{{ render_rel_input(daap_record.rel_software) }}</td>
          </tr>
        </table>
        {{ close_panel_section() }}
        {% endif %}
        {% endif %}


        {% if daap_record.os or daap_record.flavor or daap_record.app_env %}
        {% if daap_record.os != "os-notspec"  or daap_record.flavor != "flavor-notspec" or (daap_record.app_env != "appenv-notspec" and daap_record.app_env != "None") %}
        {{ open_panel_section(
        '<i class="fa fa-laptop"></i> Requirements', 'requirements', True) }}
        <table class="table table-hover">
          <tr>
            <th class="col-md-3"><i class="fa fa-fw fa-laptop"></i> OS</th>
            <td class="col-md-9">{{ bfe_daap_req_names(bfo, req_id=daap_record.os) }}</td>
          </tr>
          <tr>
            <th class="col-md-3"><i class="fa fa-fw fa-laptop"></i> Flavor</th>
            <td class="col-md-9">{{ bfe_daap_req_names(bfo, req_id=daap_record.flavor) }}</td>
          </tr>
          <tr>
            <th class="col-md-3"> <i class="fa fa-fw fa-laptop"></i> Enviroment</th>
            <td class="col-md-9">{{ bfe_daap_req_names(bfo, req_id=daap_record.app_env) }}</td>
          </tr>
        </table>
        {{ close_panel_section() }}
        {% endif %}
        {% endif %}

        {% if daap_record.__license_text__%}
        {{ open_panel_section('
        <i class="fa fa-certificate"></i> License', 2, True) }}
        <table class="table table-hover">
          <tr>
            <th class="col-md-3"><i class="fa fa-certificate fa-fw"></i> License</th>
            <td class="col-md-9"><a href="{{ daap_record.__license_text__.url }}">
                {{daap_record.__license_text__.license}}
            </a></td>
          </tr>
        </table>
        {{ close_panel_section() }}
        {% endif %}

        {% if daap_record.period or daap_record.frequency or daap_record.spatial %}
        {{ open_panel_section(
        '<i class="fa fa-globe"></i> Physical information', 3, True) }}
        <table class="table table-hover">
          {% if daap_record.period %}

          <tr>
            <th class="col-md-3"><i class="fa fa-calendar fa-fw"></i> Temporal Coverage</th>
            <td class="col-md-3">{% for period in daap_record.period %}
              <span class="text-muted">from</span> {{ period.start }} <span class="text-muted">to</span> {{ period.end }}{% if not loop.last %}; {% endif %}
              {% endfor %}</td>
          </tr>
          {% endif %}
          {% if daap_record.frequency %}
          <tr>
            <th class="col-md-3"><i class="fa fa-calendar fa-fw"></i> Frequency</th>
            <td class="col-md-9">{% for frequency in daap_record.frequency %}
              {{ frequency.size }} {{ bfe_daap_unit(bfo, frequency=frequency) }}{% if not loop.last %}; {% endif %}
              {% endfor %}</td>
          </tr>
          {% endif %}


          {% if daap_record.spatial %}
          <tr>
            <th class="col-md-3"><i class="fa fa-globe fa-fw"></i> Spatial Coverage</th>
            <td class="col-md-9">{{ bfe_daap_spatial(bfo, spatial=daap_record.spatial) }}
              <p>
              {% for spatial in daap_record.spatial %}
              {{ spatial.west }} (western most longitude), {{ spatial.east }} (eastern most longitude), {{ spatial.north }} (northern most latitude), {{ spatial.south }} (southern most latitude) {% if not loop.last %}; {% endif %}
              {% endfor %}
              </p>
            </td>
          </tr>
          {% endif %}
        </table>
          {{ close_panel_section() }}
          {% endif %}

          {% if daap_record.communities %}
          {{ open_panel_section('
          <i class="fa fa-users"></i>Comunnities', 4, True) }}
          <table class="table table-hover">
          </tr>
            <th class="col-md-3"><i class="fa fa-users fa-fw"></i> Communities</th>
            <td class="col-md-9">{{ bfe_daap_community(bfo, record=daap_record) }}</td>
          </tr>
        </table>
          {{ close_panel_section() }}
          {% endif %}

          {% if daap_record.related_identifiers %}
          {{ open_panel_section('
          <i class="fa fa-bars"></i>Related identifiers', 5, True) }}
          <table class="table table-hover">
            <tr>
            
              <th class="col-md-3"><i class="fa fa-bars fa-fw"></i> Related identifiers</th>
              <td class="col-md-9">
                {% for relid in daap_record.related_identifiers %}
              <span class="label label-primary" style="display: inline-block; margin: 5px 5px;">
                <a href="{{ url_for('search.search', p='relid.identifier:' + relid.identifier) }}">
                  {{ relid.identifier }}
                </a>
              </span>
              {% endfor %}
            </td>
          </tr>
        </table>
          {{ close_panel_section() }}
          {% endif %}

          {% if daap_record.subjects %}
          {{ open_panel_section('
          <i class="fa fa-tags"></i> Subjects', 6, True) }}
          <table class="table table-hover">
            <tr>
            <th class="col-md-3"><i class="fa fa-tags fa-fw"></i> Subjects</th>
            <td class="col-md-9">
              {% for term in daap_record.subjects %}
              <span class="label label-primary" style="display: inline-block; margin: 5px 5px;">
                {{ term.term }} (<a href="{{ url_for('search.search', p='term.identifier:' + term.identifier) }}">{{ term.identifier }}</a>) {% if not loop.last %}; {% endif %}
              </span>
              {% endfor %}
            </td>
          </tr>
          </table>
          {{ close_panel_section() }}
          {% endif %}
        </div>
      </div>
    </div>
    {% endblock %}

    <div class="spacer40"></div>

    {% if daap_files and show_files %}
    {% set allowed = not daap_files[0].is_restricted(current_user)[0] %}
    <div class="spacer40"></div>

    {% block files %}
    {% if allowed %}
    <h2><span class="badge" style="font-size:inherit;">{{ daap_files|length }}</span> Files{% if allowed %}{% endif %}</h2>
    <div class="spacer30"></div>
    {% for row in daap_files|sort(attribute='comment')|batch(2) %}
    <div class="row">

      {% for file in row %}
      <div class="col-md-6">
        <a class="btn btn-primary  file-resource"  href="{{ file.url }}">
          <div class="col-xs-2 text-center">
            <span class="file-resource-type">
              <i class="fa fa-download fa-2x" aria-hidden="true"></i><br/>
              <strong class="uppercase">{{ file.format[1:] }}</strong>
            </span>
          </div>
          <div class="col-xs-8">
            <span class="file-resource-text">
              <strong>
                {{ file.description if file.description else file.get_full_name() }}
              </strong>
            </span>
          </div>
          <div class="col-xs-2">
            <span class="file-resource-download">
              {{ file.size|filesizeformat if file.size }}
            </span>
          </div>
        </a>
      </div>
      {% endfor %}
    </div>
    {% endfor %}
    {% elif (daap_record.access_right is equalto 'embargoed') %}
    <h3>Access to this record is allowed from {{ daap_record.embargo_date }}.</h3>
    {% elif (daap_record.access_right is equalto 'restricted')  %}
    <h3>Access to this record is allowed under the record conditions. Request access to some of the allowed groups
      ({{ bfe_daap_group_names(bfo, groups=daap_record.access_groups) }}) to get the permission to access the record.</h3>
    {% elif (daap_record.access_right is equalto 'closed')  %}
    <h3>Access to this record is not allowed.</h3>
    {% endif %}
    {% endblock %}
    {% endif %}
  </div>
