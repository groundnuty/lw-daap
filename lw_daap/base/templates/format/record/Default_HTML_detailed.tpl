{% from "format/record/record_macros.tpl" import render_authors, render_access_rights %}

{% include "lw_daap/pids/doi_modal.html" %}

<div class="record-details">
  {% block header %}
  <div class="row">
    <div class="col-sm-12 col-md-12">
      <h1>{{ daap_record.title }}</h1>
    </div>
  </div>
  <div class="row">
    <div class="col-sm-9 col-md-9">
      <h3>Published by  {{ render_authors(daap_record, 4) }}</h3>
      {% if daap_record.access_right %}
      <h4>Access {{ render_access_rights(daap_record) }}</h4>
      {% endif %}

      {% if daap_record.license %}
        <h4>License: {% if daap_record.license.url %}<a href="{{ daap_record.license.url }}">{% endif -%}
            {{ daap_record.license.license }}{% if daap_record.license.url %}</a>{% endif -%}
        </h4>
      {% endif %}
      {% if daap_record.access_conditions %}
        {{ daap_record.access_conditions }}
      {% endif %}
      <div class="record-abstract">
        {% if daap_record.description %}
          <h4>Description</h4>
          {{ daap_record.description }}
        {% endif %}
      </div>
    </div>
    <div class="col-sm-3 col-md-3 well">
      {% include "lw_daap/pids/doi_info.html" %}
    </div>
  </div>
  {% endblock %}

  <div>
    {% block metadata %}
    <h2>Metadata</h2>
    <div class="table-responsive">
      <table class="table table-striped">
        <tbody>
          {% if daap_record.upload_type %}
            <tr><td class="key">Type</td><td class="value">{{ daap_record.upload_type }}</td></tr>
          {% endif %}
          {% if daap_record.communities %}
            <tr><td class="key">Communities</td><td class="value">{{ bfe_daap_community(bfo, daap_record=daap_record) }}</td></tr>
          {% endif %}
          {% if daap_record.publication_date %}
            <tr><td class="key">Publication date</td><td class="value">{{ daap_record.publication_date }}</td></tr>
          {% endif %}
          {% if daap_record.doi %}
            <tr><td class="key">DOI</td><td class="value">{{ daap_record.doi }}</td></tr>
          {% endif %}
          {% if daap_record.__license_text__%}
            <tr><td class="key">License</td><td class="value"><a href="{{ daap_record.__license_text__.url }}">{{daap_record.__license_text__.license}}</a></td></tr>
          {% endif %}
          {% if daap_record.keywords %}
            <tr><td class="key">Keywords</td><td class="value">
            {% for keyword in daap_record['keywords'] %}
              <span class="label label-default"><a href="{{ url_for('search.search', p='keyword:' + keyword) }}">{{ keyword }}</a></span>
            {% endfor %}
            </td></tr>
          {% endif %}
          {% if daap_record.notes %}
            <tr><td class="key">Additional notes</td><td class="value">{{ daap_record.notes }}</td></tr>
          {% endif %}
          {% if daap_record.period %}
            <tr><td class="key">Temporal Coverage</td><td class="value">
            {% for period in daap_record.period %}
              {{ period.start }} - {{ period.end }}{% if not loop.last %}; {% endif %}
            {% endfor %}
          {% endif %}
          {% if daap_record.spatial %}
            <tr><td class="key">Spatial Coverage</td><td class="value">{{ daap_record.spatial }}</td></tr>
          {% endif %}
          {% if daap_record.related_identifiers %}
            <tr><td class="key">Related identifiers</td><td class="value">
            {% for relid in daap_record.related_identifiers %}
              <span class="label label-default"><a href="{{ url_for('search.search', p='relid.identifier:' + relid.identifier) }}">{{ relid.identifier }}</a></span>
            {% endfor %}
            </td></tr>
          {% endif %}
          {% if daap_record.subjects %}
            <tr><td class="key">Subjects</td><td class="value">
            {% for term in daap_record.subjects %}
              {{ term.term }} {{ ' (' ~ term.identifier ~ ')' if term.identifier }}{% if not loop.last %}; {% endif %}
            {% endfor %}
            </td></tr>
          {% endif %}
          {% if daap_files %}
            <tr><td class="key">Size</td><td class="value">
            {{ bfe_size(bfo, files=daap_files) | filesizeformat }} </td></tr>
          {% endif %}
        </tbody>
      </table>
    </div>
    {% endblock %}

    {% if daap_files %}
      {% set record_owner = current_user.id == daap_record.get('owner', {}).get('id', -1)|int %}
      {% set allowed = (record_owner or
                       (daap_record.access_right == 'open') or
                       (daap_record.access_right == 'embargoed' and
                         bfe_datetime(bfo, embargo_date=daap_record.embargo_date)))
      %}
      {% block files %}
      <h2>Files{% if allowed %} ({{ daap_files|length }}){% endif %}</h2>
        {% if allowed %}
        {% for row in daap_files|sort(attribute='comment')|batch(2) %}
        <div class="row">
          {% for file in row %}
            <div class="file-resource col-sm-6">
              <div class="file-resource-type col-sm-2 text-center">
                <span class="fa fa-stack fa-2x">
                <i class="fa fa-file-o fa-2x" aria-hidden="true"></i>
                <strong class="fa fa-stack-1x uppercase" style="margin-top: .5em; font-size: 0.6em;">{{ file.format }}</strong>
                </span>
              </div>
              <div class="file-resource-text col-sm-8">
                <strong>
                {{ file.description if file.description else file.get_full_name() }}
                </strong>
              </div>
              <a class="file-resource-download col-sm-2 text-center" href="{{ file.url }}">
                <span class="fa fa-download fa-2x" aria-hidden="true"></span></br>
                {{ file.size|filesizeformat if file.size }}
              </a>
            </div>
          {% endfor %}
        </div>
        {% endfor %}
      {% elif (daap_record.access_right is equalto 'embargoed') %}
        <h3>Access to this record is allowed from {{ daap_record.embargo_date }}.</h3>
      {% else %}
        <h3>Access to this record is allowed under the record conditions.</h3>
      {% endif %}
      {% endblock %}
    {% endif %}
  </div>
</div>
