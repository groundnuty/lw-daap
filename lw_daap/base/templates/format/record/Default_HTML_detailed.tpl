{% from "format/record/record_macros.tpl" import render_authors, render_access_rights %}

{% include "lw_daap/pids/doi_modal.html" %}

<div class="record-details">
  {% block header %}
  <div class="row">
    <div class="col-sm-12 col-md-12">
      <h1>{{ record.title }}</h1>
    </div>
  </div> 
  <div class="row">
    <div class="col-sm-9 col-md-9">
      <h3>Published by  {{ render_authors(record, 4) }}</h3>
      {% if record.access_right %}
      <h4>Access {{ render_access_rights(record) }}</h4>
      {% endif %}
      {% if record.__license_text__ %}
      <h4>License: <a href="{{ record.__license_text__.url }}">{{record.__license_text__.license}}</a></h4>
      {% endif %}
      {% if record.access_conditions %}
      {{ record.access_conditions }}
      {% endif %}
      <div class="record-abstract">
        {% if record.description %}
        <h4>Description</h4>
        {{ record.description }}
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
          {% if record.upload_type %}
            <tr><td class="key">Type</td><td class="value">{{ record.upload_type }}</td></tr>
          {% endif %}
          {% if record.communities %}
            <tr><td class="key">Communities</td><td class="value">{{ bfe_community(bfo, record=record) }}</td></tr>
          {% endif %}
          {% if record.publication_date %}
            <tr><td class="key">Publication date</td><td class="value">{{ record.publication_date }}</td></tr>
          {% endif %}
          {% if record.doi %}
            <tr><td class="key">DOI</td><td class="value">{{ record.doi }}</td></tr>
          {% endif %}
          {% if record.__license_text__%}
            <tr><td class="key">License</td><td class="value"><a href="{{ record.__license_text__.url }}">{{record.__license_text__.license}}</a></td></tr>
          {% endif %}
          {% if record.keywords %}
            <tr><td class="key">Keywords</td><td class="value">
            {% for keyword in record['keywords'] %}
              <span class="label label-default"><a href="{{ url_for('search.search', p='keyword:' + keyword) }}">{{ keyword }}</a></span>
            {% endfor %}
            </td></tr>
          {% endif %}
          {% if record.notes %}
            <tr><td class="key">Additional notes</td><td class="value">{{ record.notes }}</td></tr>
          {% endif %}
          {% if record.period %}
            <tr><td class="key">Temporal Coverage</td><td class="value">{{ record.period.start }} - {{ record.period.end }}</td></tr>
          {% endif %}
          {% if record.spatial %}
            <tr><td class="key">Spatial Coverage</td><td class="value">{{ record.spatial }}</td></tr>
          {% endif %}
          {% if record.related_identifiers %}
            <tr><td class="key">Related identifiers</td><td class="value">
            {% for relid in record.related_identifiers %}
              <span class="label label-default"><a href="{{ url_for('search.search', p='relid.identifier:' + relid.identifier) }}">{{ relid.identifier }}</a></span>
            {% endfor %}
            </td></tr>
          {% endif %}   
          {% if record.subjects %}
            <tr><td class="key">Subjects</td><td class="value">
            {% for term in record.subjects %}
              {{ term.term }} {{ ' (' ~ term.identifier ~ ')' if term.identifier }}{% if not loop.last %}; {% endif %}
            {% endfor %}
            </td></tr>
          {% endif %}
          {% if show_files %}
            {% if record.fft %}
              <tr><td class="key">Size</td><td class="value">
              {{ bfe_size(bfo, record=record) | filesizeformat }} </td></tr>
            {% endif %}
          {% endif %}
        </tbody>
      </table>
    </div>
    {% endblock %}
    {% if show_files %}
      {% set record_owner = current_user.id == record.get('owner', {}).get('id', -1)|int %}
      {% set allowed = (record_owner or 
                       (record.access_right == 'open') or
                       (record.access_right == 'embargoed' and
                         bfe_datetime(bfo, embargo_date=record.embargo_date)))
      %}
      {% if record.fft %}
        {% block files %}
        <h2>Files{% if allowed %} ({{ record.fft|length }}){% endif %}</h2>
          {% if allowed %}
          {% for row in record.fft|batch(2) %}
          <div class="row">
            {% for file in row %}
              <div class="file-resource col-sm-6">
                <div class="file-resource-type col-sm-2 text-center">
                  <span class="fa fa-stack fa-2x">
                  <i class="fa fa-file-o fa-2x" aria-hidden="true"></i>
                  <strong class="fa fa-stack-1x uppercase" style="margin-top: .5em; font-size: 0.6em;">{{ bfe_fileextension(bfo, url=file.url) }}</strong>
                  </span>
                </div>
                <div class="file-resource-text col-sm-8">
                  <strong>
                  {{ file.description if file.description else bfe_filename(bfo, url=file.url) }}
                  </strong>
                </div>
                <a class="file-resource-download col-sm-2 text-center" href="{{ file.url }}">
                  <span class="fa fa-download fa-2x" aria-hidden="true"></span></br>
                  {{ file.file_size|filesizeformat if file.file_size }}
                </a>
              </div>
            {% endfor %}
          </div>
          {% endfor %}
        {% elif (record.access_right is equalto 'embargoed') %}
          <h3>Access to this record is allowed from {{ record.embargo_date }}.</h3>
        {% else %}
          <h3>Access to this record is allowed under the record conditions.</h3>
        {% endif %}
        {% endblock %}
      {% endif %}
    {% endif %}
  </div>
</div>
