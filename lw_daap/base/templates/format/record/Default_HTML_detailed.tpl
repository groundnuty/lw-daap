{% from "format/record/record_macros.tpl" import render_authors, render_access_rights %}

<div class="records-details">
  <div class="">
    {% block header %}
    <h1>{{ record.title }}</h1>
    <div class="record-published">
      <h3>Published by  {{ render_authors(record, 4) }}</h3>
      {% if record.access_right %}
      <h4>Access {{ render_access_rights(record) }}</h4>
      {% endif %} 
      {% if record.__license_text__ %}
      <h4>License: <a href="{{ record.__license_text__.url }}">{{record.__license_text__.license}}</a></h4>
      {% endif%}
    </div>
    <div> {# FIXME: add some space for this to breath #}
        {% if record.description %}
            {{ record.description }}
        {% endif %}
    </div>
    {% endblock %}

    {% block metadata %}
    <h2>Metadata</h2>
    {# FIXME: good class for the table #}
    <table class="table table-bordered table-condensed table-dgu-fixed-size dgu-table">
      <tbody>
        {% if record.upload_type %}
          <tr><td class="key">Type</td><td class="value">{{ record.upload_type }}</td></tr>
        {% endif %}
        {% if record.communities %}
          <tr><td class="key">Communities</td>
              <td class="value">{{ record.communities|join(', ')}} </td>
          </tr>
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
          <tr><td class="key">Keywords</td><td class="value">{{ record.keywords|join('; ') }}</td></tr>
        {% endif %}
        {% if record.period %}
          <tr><td class="key">Temporal Coverage</td><td class="value">{{ record.period.start }} - {{ record.period.end }}</td></tr>
        {% endif %}
        {% if record.fft %}
          <tr><td class="key">Size</td><td class="value">
            SUM SIZES{# record.fft|map(attribute='file_size', int)|join(', ') #}</td></tr>
        {% endif %}
      </tbody>
    </table>
    {% endblock %}

    {% if record.fft %}
    {% block files %}
    <h2>Files ({{ record.fft|length }})</h2>
    {% for row in record.fft|batch(2) %}
      <div class="row">
        {% for file in row %}
        <div class="col-sm-6">
            <div class=""> 
                <a href="{{ file.url }}"><div class="" style="width: 20%;">
                    <i class="glyphicon glyphicon-file" aria-hidden="true" style="font-size: 3em;"></i><span class="format-name">.csv<span>
                </div></a>
                <div class="" style="width: 80%;">
                    {{ file.description }} 
                </div>
        </div>
        {% endfor %}
      </div>
    {% endfor %}
    {% endblock %}
    {% endif %}
  </div> <!-- class="" -->
</div>
