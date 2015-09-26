{% from "format/record/record_macros.tpl" import
render_authors, render_access_rights,
render_deposition_type %}

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
    <div class="col-sm-6 col-md-6">
      <h4 style="margin-top: 0px">{{ render_authors(daap_record, 4) }}</h4>
    </div>
    <div class="col-sm-6 col-md-6 pull-right">
      <a class="btn btn-glassy btn-sharp btn-raised" href="#"><i class="fa fa-barcode"></i> Mint Doi</a>
      <a class="btn btn-forest btn-sharp btn-raised" href="#"><i class="fa fa-pencil-square-o"></i> Edit</a>
      <a class="btn btn-sunshine btn-sharp btn-raised" href="#"><i class="fa fa-play-circle-o"></i> Run</a>
    </div>
  </div>

  <div class="spacer30"></div>

  <div class="row">
    {% if daap_files and show_files %}
    <div class="col-sm-3 col-md-3">
      <div class="panel-forest panel-sharp">
        <div class="panel-heading">
          <i class="fa fa-book"></i> Summary
        </div>
        <div class="panel-body">
          <h4>Publication  Date</h4>{{ daap_record.publication_date }}
          {% include "lw_daap/pids/doi_info.html" %}
          <h4>Access</h4><h4> {{ render_access_rights(daap_record) }}</h4>
          <h4>Record type</h4><h4> {{ render_deposition_type(daap_record) }}</h4>

        </div>
      </div>
    </div>
    {% endif %}

    <div class="col-sm-9 col-md-9">
      {#
      {% if daap_record.license %}
      <h4>License: {% if daap_record.license.url %}<a href="{{ daap_record.license.url }}">{% endif -%}
          {{ daap_record.license.license }}{% if daap_record.license.url %}</a>{% endif -%}
      </h4>
      {% endif %}
      {% if daap_record.access_conditions %}
      {{ daap_record.access_conditions }}
      {% endif %}
      {% if daap_record.access_groups %}
      {{ bfe_daap_group_names(bfo, groups=daap_record.access_groups) }}
      {% endif %}
      #}
      <div class="deposition-wrapper">
        <div class="panel panel-deposit panel-sharp">
          <div class="panel-heading">
            <a data-toggle="collapse" class="panel-toggle" href="#collapse-1">
              <i class="fa fa-info"></i>Basic information
              <span class="pull-right show-on-collapsed">
                <i class="fa fa-chevron-down"></i>
              </span>
              <span class="pull-right hide-on-collapsed">
                <i class="fa fa-chevron-up"></i>
              </span>
            </a>
          </div>
          <div id="collapse-1" class="panel-collapse collapse in">
            <div class="panel-body">
              <div class="row" style="margin-bottom: 30px;">
                {% if daap_record.description %}
                <div class="col-md-3">
                  <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
                    <i class="fa fa-pencil fa-fw"></i> Description
                  </span>
                </div>
                <div class="col-md-9">
                  {{ daap_record.description }}
                </div>
                {% endif %}
              </div>
              <div class="row" style="margin-bottom: 30px;">
                {% if daap_record.keywords %}
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
                {% endif %}
              </div>
              <div class="row" style="margin-bottom:30px;">
                {% if daap_record.notes %}
                <div class="col-md-3">
                  <span style="font-size: 1.3em; font-weight: 700; white-space: nowrap;">
                    <i class="fa fa-pencil fa-fw"></i> Additional Notes
                  </span>
                </div>
                <div class="col-md-9">
                  {{ daap_record.notes }}
                </div>
                {% endif %}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
  {% endblock %}

  <div class="spacer40"></div>

  {#
  {% block metadata %}
  <h2>Metadata</h2>
  <div class="table-responsive">
    <table class="table table-striped">
      <tbody>
      {% if daap_record.communities %}
      <tr><td class="key">Communities</td><td class="value">{{ bfe_daap_community(bfo, record=daap_record) }}</td></tr>
      {% endif %}


      {% if daap_record.__license_text__%}
      <tr>
        <td class="key">License</td>
        <td class="value">
          <a href="{{ daap_record.__license_text__.url }}">
            {{daap_record.__license_text__.license}}
          </a>
        </td>
      </tr>
      {% endif %}

      {% if daap_record.period %}
      <tr>
        <td class="key">Temporal Coverage</td>
        <td class="value">
          {% for period in daap_record.period %}
          {{ period.start }} - {{ period.end }}{% if not loop.last %}; {% endif %}
          {% endfor %}
        </td>
      </tr>
      {% endif %}
      {% if daap_record.spatial %}
      <tr>
        <td class="key">Spatial Coverage</td><
        <td class="value">{{ daap_record.spatial }}</td>
      </tr>
      {% endif %}
      {% if daap_record.related_identifiers %}
      <tr>
        <td class="key">Related identifiers</td>
        <td class="value">
          {% for relid in daap_record.related_identifiers %}
          <span class="label label-default">
            <a href="{{ url_for('search.search', p='relid.identifier:' + relid.identifier) }}">
              {{ relid.identifier }}
            </a>
          </span>
          {% endfor %}
        </td>
      </tr>
      {% endif %}
      {% if daap_record.subjects %}
      <tr>
        <td class="key">Subjects</td>
        <td class="value">
          {% for term in daap_record.subjects %}
          {{ term.term }} {{ ' (' ~ term.identifier ~ ')' if term.identifier }}{% if not loop.last %}; {% endif %}
          {% endfor %}
        </td>
      </tr>
      {% endif %}
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

      {% if daap_files %}
      <tr>
        <td class="key">Size</td>
        <td class="value">
          {{ bfe_daap_filesize(bfo, files=daap_files) | filesizeformat }}
        </td>
      </tr>
      {% endif %}
      </tbody>
    </table>
  </div>
  {% endblock %}
  #}
  {% if daap_files and show_files %}
  {% set allowed = not daap_files[0].is_restricted(current_user)[0] %}
  <div class="spacer40"></div>

   {% block files %}
  {% if allowed %}
   <h2>Files{% if allowed %} ({{ daap_files|length }}){% endif %}</h2>
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
