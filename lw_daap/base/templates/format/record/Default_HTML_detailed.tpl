{% from "format/record/record_macros.tpl" import render_authors,
render_access_rights,
render_deposition_type,
open_panel_section, close_panel_section
%}

{% include "lw_daap/pids/doi_modal.html" %}

{% if not daap_record %}
{% set daap_record = record %}
{% endif %}

<div class="record-details">
  {% block header %}
  <div class="row">

    <div class="col-sm-12 col-md-12">
      <h2>{{ daap_record.title }}</h2>
    </div>
    <div class="col-sm-12">
      <h4 style="margin-top: 0px">{{ render_authors(daap_record, 4) }}</h4>
    </div>
  </div>

  <div class="spacer30"></div>

  <div class="row">
    {% if daap_files and show_files %}
    <div class="col-sm-12 col-md-3">

{% if current_user.get_id() == daap_record.get('owner', {}).get('id', -1)|int %}
{% if not daap_record.doi and not bfe_is_doi_being_minted(bfo, recid=recid) %}
      <button class="btn btn-block btn-lg btn-glassy btn-sharp btn-raised" 
      data-toggle="modal" data-target="#doi-confirm-dialog">
      <i class="fa fa-barcode"></i> Mint Doi</button>
{% endif %}
      <a class="btn btn-block btn-lg btn-forest btn-sharp btn-raised" href="{{ url_for('webdeposit.edit', uuid=daap_record.owner.deposition_id|int) }}"><i class="fa fa-pencil-square-o"></i> Edit</a>
{% endif %}
      <a class="btn btn-block btn-lg btn-sunshine btn-sharp btn-raised" href="#"><i class="fa fa-play-circle-o"></i> Run</a>
      <div class="spacer20"></div>
      <div class="panel-forest panel-sharp">
        <div class="panel-heading">
          <i class="fa fa-book"></i> Summary
        </div>
        <div class="panel-body">
          <h4>Publication  Date</h4>{{ daap_record.publication_date }}
          {% include "lw_daap/pids/doi_info.html" %}
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
        {{ open_panel_section(
        '<i class="fa fa-info"></i> Basic information', 1, True) }}
        {% if daap_record.description %}
        <div class="row" style="margin-bottom: 30px;">
          <div class="col-md-3">
            <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
              <i class="fa fa-pencil fa-fw"></i> Description
            </span>
          </div>
          <div class="col-md-9">
            {{ daap_record.description }}
          </div>
        </div>
        {% endif %}

        {% if daap_record.keywords %}
        <div class="row" style="margin-bottom: 30px;">
          <div class="col-md-3">
            <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
              <i class="fa fa-tags fa-fw"></i> Keywords
            </span>
          </div>
          <div class="col-md-9">
            {% for keyword in daap_record['keywords'] %}
            <span class="label label-forest" style="display: inline-block; margin: 5px 5px;">
              <a href="{{ url_for('search.search', p='keyword:' + keyword) }}">{{ keyword }}</a>
            </span>
            {% endfor %}
          </div>
        </div>
        {% endif %}

        {% if daap_record.notes %}
        <div class="row" style="margin-bottom:30px;">
          <div class="col-md-3">
            <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
              <i class="fa fa-pencil fa-fw"></i> Additional Notes
            </span>
          </div>
          <div class="col-md-9">
            {{ daap_record.notes }}
          </div>

        </div>
        {% endif %}
        {{ close_panel_section() }}

        {{ open_panel_section('
        <i class="fa fa-certificate"></i> License', 2, True) }}
        {% if daap_record.__license_text__%}
        <div class="row" style="margin-bottom: 30px;">
          <div class="col-md-3">
            <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
              <i class="fa fa-certificate fa-fw"></i> License
            </span>
          </div>
          <div class="col-md-9">
            <a href="{{ daap_record.__license_text__.url }}">
              {{daap_record.__license_text__.license}}
            </a>
          </div>
        </div>
        {% endif %}
        {{ close_panel_section() }}
        {{ open_panel_section(
        '<i class="fa fa-globe"></i> Physical information', 3, True) }}
        {% if daap_record.period %}
        <div class="row" style="margin-bottom: 30px;">
          <div class="col-md-3">
            <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
              <i class="fa fa-calendar fa-fw"></i> Temporal Coverage
            </span>
          </div>
          <div class="col-md-9">
            {% for period in daap_record.period %}
            <div class="col-xs-3"><span class="text-muted">from</span> {{ period.start }}</div>
            <div class="col-xs-3"><span class="text-muted">to</span> {{ period.end }}</div>
            <div class="col-xs-6">&nbsp;</div>
            {% endfor %}
          </div>
        </div>
        {% endif %}
        {% if daap_record.frequency %}
        <div class="row" style="margin-bottom: 30px;">
          <div class="col-md-3">
            <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
              <i class="fa fa-calendar fa-fw"></i> Frequency
            </span>
          </div>
          <div class="col-md-9">
            {{ daap_record.frequency.size }} {{ bfe_daap_unit(bfo, frequency=daap_record.frequency) }}
          </div>
        </div>
        {% endif %}


        {% if daap_record.spatial %}
        <div class="row" style="margin-bottom: 30px;">
          <div class="col-md-3">
            <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
              <i class="fa fa-globe fa-fw"></i> Spatial Coverage
            </span>
          </div>
          <div class="col-md-9">
            {{ daap_record.spatial }}
          </div>
        </div>
        {% endif %}
        {{ close_panel_section() }}

        {{ open_panel_section('
        <i class="fa fa-users"></i>Comunnities', 4, True) }}
        {% if daap_record.communities %}
        <div class="row" style="margin-bottom: 30px;">
          <div class="col-md-3">
            <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
              <i class="fa fa-users fa-fw"></i> Communities
            </span>
          </div>
          <div class="col-md-9">
            {{ bfe_daap_community(bfo, record=daap_record) }}
          </div>
        </div>
        {% endif %}
        {{ close_panel_section() }}

        {{ open_panel_section('
        <i class="fa fa-bars"></i>Related identifiers', 5, True) }}
        {% if daap_record.related_identifiers %}
        <div class="row" style="margin-bottom: 30px;">
          <div class="col-md-3">
            <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
              <i class="fa fa-bars fa-fw"></i> Related identifiers
            </span>
          </div>
          <div class="col-md-9">
            {% for relid in daap_record.related_identifiers %}
            <span class="label label-forest" style="display: inline-block; margin: 5px 5px;">
              <a href="{{ url_for('search.search', p='relid.identifier:' + relid.identifier) }}">
                {{ relid.identifier }}
              </a>
            </span>
            {% endfor %}
          </div>
        </div>
        {% endif %}
        {{ close_panel_section() }}

        {{ open_panel_section('
        <i class="fa fa-tags"></i> Subjects', 6, True) }}
        {% if daap_record.subjects %}
        <div class="row" style="margin-bottom: 30px;">
          <div class="col-md-3">
            <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
              <i class="fa fa-tags fa-fw"></i> Subjects
            </span>
          </div>
          <div class="col-md-9">
            {% for term in daap_record.subjects %}
            {{ term.term }} {{ ' (' ~ term.identifier ~ ')' if term.identifier }}{% if not loop.last %}; {% endif %}
            {% endfor %}
          </div>
        </div>
        {% endif %}
        {{ close_panel_section() }}
        {#
        {% if daap_record.os or daap_record.flavor or daap_record.app_env%}   
        <tr>
          <td class="key">Requirements</td>
          <td class="value">
            {% if daap_record.os %}<p>OS: {{bfe_daap_req_names(bfo, req_id=daap_record.os)}}</p>{% endif %}    
            {% if daap_record.flavor %}<p>{{bfe_daap_req_names(bfo, req_id=daap_record.flavor)}}</p>{% endif %}    
            {% if daap_record.app_env %}<p>Application environment: {{bfe_daap_req_names(bfo, req_id=daap_record.app_env)}}</p>{% endif %}    
          </td>
        </tr>
        {% endif %}
        #}

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
      <a class="btn btn-forest btn-raised file-resource"  href="{{ file.url }}">
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
