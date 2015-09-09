{% from "format/record/record_macros.tpl" import render_authors, render_access_rights %}


<div class="record-details">
  {% block header %}
  <div class="row">
    <div class="col-sm-12 col-md-12">
      <h1>{{ record.title }}</h1>
    </div> <!-- col 12 -->
  </div> <!-- row -->
  <div class="row">
    <div class="col-sm-9 col-md-9">
      <h3>Published by  {{ render_authors(record, 4) }}</h3>
      {% if record.access_right %}
        <h4>Access {{ render_access_rights(record) }}</h4>
      {% endif %}
      {% if record.__license_text__ %}
        <h4>License: <a href="{{ record.__license_text__.url }}">{{record.__license_text__.license}}</a></h4>
      {% endif%}
      {# FIXME: add some space for this to breath #}
      <div class="record-abstract">
        {% if record.description %}
            {{ record.description }}
        {% endif %}
      </div> <!-- record-abstract -->
    </div> <!-- col 9 -->
    <button type="button" class="btn btn-lg btn-default well pull-right">Mint DOI</button>
  </div> <!-- row -->
  {% endblock %}
  <div class="">
    <br/>
    <br/>
    {% block metadata %}
    <h2>Metadata</h2>
    {# FIXME: good class for the table #}
    <br/>
    <div class="table-responsive">
    <table class="table table-striped">
      <tbody>
        {% if record.upload_type %}
          <tr><td class="key">Type</td><td class="value">{{ record.upload_type }}</td></tr>
        {% endif %}
        {% if record.communities %}
          <tr><td class="key">Communities</td><td class="value"> 
            {{ bfe_community(bfo, record=record) }}
        </td></tr>
        {% endif %}
        {% if record.publication_date %}
          <tr><td class="key">Publication date</td><td class="value">{{ record.publication_date }}</td></tr>
        {% endif %}
        {% if record.doi %}
          <tr><td class="key">DOI</td><td class="value">{{ record.doi }}</td></tr>
        {% endif %}
        {% if record.__license_text__%}
          <tr><td class="key">License</td><td class="value"><a href="{{ record.__license_text__.url }}">
            {{record.__license_text__.license}}</a></td></tr>
        {% endif %}
        {% if record.keywords %}
          <tr><td class="key">Keywords</td><td class="value">
                 {% for keyword in record['keywords'] %}
                    <span class="label label-default"><a href="{{ url_for('search.search', p='keyword:' + keyword) }}">{{ keyword }}</a></span>
                 {% endfor %}
          </td></tr>
        {% endif %}
        {% if record.period %}
          <tr><td class="key">Temporal Coverage</td><td class="value">{{ record.period.start }} - {{ record.period.end }}</td></tr>
        {% endif %}
        {% if record.period %}
          <tr><td class="key">Spatial Coverage</td><td class="value">{{ record.spatial }}</td></tr>
        {% endif %}
        {% if record.fft %}
          <tr><td class="key">Size</td><td class="value">
            {{ bfe_size(bfo, record=record) | filesizeformat }} </td></tr>
        {% endif %}
      </tbody>
    </table>
    </div>
    {% endblock %}
    <br/>
    <br/>
    {% set record_owner = current_user.id == record.get('owner', {}).get('id', -1)|int %}
    {% if record.fft %}
    {% block files %}
    {% if (record.access_right is equalto 'closed') and not record_owner %}
    <h2>Files</h2>
    <h3>Access to this record is not allowed under the record conditions.</h3>
    {% elif (record.access_right is equalto 'restricted') and not record_owner %}
    <h2>Files</h2>
    <h3>Access to this record is not allowed under the record conditions.</h3>
    {% elif (record.access_right is equalto 'embargoed') and not record_owner %}
        {% if bfe_datetime(bfo, embargo_date=record.embargo_date) %}
            <h2>Files</h2>
            <h3>Access to this record is allowed from {{ record.embargo_date }}.</h3>
        {% else %}       
            {% for row in record.fft|batch(2) %}
            <h2>Files ({{ record.fft|length }})</h2> <br/>
            <div class="row">
                {% for file in row %}
                <div class="col-sm-6">
                    <a href="{{ file.url }}"><span class="glyphicon glyphicon-file" aria-hidden="true"></span> {{ file.description }}</a>
                </div>
                {% endfor %}
            </div>
            {% endfor %}
        {% endif %}
    {% else %}       
        {% for row in record.fft|batch(2) %}
        <h2>Files ({{ record.fft|length }})</h2><br />
        <div class="row">
            {% for file in row %}
            <div class="col-xs-8">
               <div class="btn-group btn-group-lg" role="group" aria-label="...">
                  <span class="btn btn-primary disabled"><strong>CSV</strong></span>
                  <span class="btn btn-default disabled"><strong>{{ file.description if file.description else "-null-"}}</strong></span>
                  <a class="btn btn-default" href="{{ file.url }}"><span class="fa fa-download" aria-hidden="true"></span> {{file.file_size|filesizeformat}}</a>
                </div>
            </div>
            {% endfor %}
        </div>
        {% endfor %}
    {% endif %}
    {% endblock %}
    {% endif %}
  </div>
</div>
