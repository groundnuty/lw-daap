
<div class="records-details">

  <div class="">
    {% block header %}
    <h1>{{ record.title }}</h1>
    <div class="record-published">
      {# TODO: format this with search links #}
      Published by {{ record.authors|join('; ', attribute='name') }}
      {% if record.__license_text__ %}
         License: <a href="{{ record.__license_text__.url }}">
            {{record.__license_text__.license}}</a>
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
        {% if record.publication_date %}
          <tr><td class="key">Publication date</td><td class="value">{{ record.publication_date }}</td>
        {% endif %}
        {% if record.doi %}
          <tr><td class="key">DOI</td><td class="value">{{ record.doi }}</td>
        {% endif %}
        {% if record.__license_text__%}
          <tr><td class="key">License</td><td class="value"><a href="{{ record.__license_text__.url }}">
            {{record.__license_text__.license}}</a></td>
        {% endif %}
        {% if record.keywords %}
          <tr><td class="key">Keywords</td><td class="value">{{ record.keywords|join('; ') }}</a></td>
        {% endif %}
      </tbody>
    </table>
    {% endblock %}

    {% if record.fft %}
    {% block files %}
    <h2>Files</h2>
    {{ record.fft.file_size }}
    {{ record.fft.description }}
    {{ record.fft.url }}
    {% for f in record.fft %}
        <p>Here!</p>
        <p>{{ f }} </p>
    {% endfor %}
    {% endblock %}
    {% endif %}
  </div> <!-- class="" -->
</div>
