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

#
# (c) 2015 aeonium. 
#

{%- macro render_rel_input(rel_inputs) %}
{% for rel in rel_inputs %}
  <p>{{ bfe_daap_record(bfo, rec_id=rel)}}</p>
{% endfor %}
{% endmacro -%}


{# TODO: use the max parameter #}
{%- macro render_authors(record, max=None) %}
{% if record.authors %}
{% for author in record.authors %}
<a href="{{ url_for('search.search', p='author:"' + author.name + '"') }}">
  {{ author.name }}
{% if author.orcid %}
<a href="http://orcid.org/{{author.orcid}}" title="ORCID" target="_blank" style="color:#A6CE39;">
<sup>orcid</sup></a>
{% endif %}
{% if author.affiliation %}
<a href="{{ url_for('search.search', p='affiliation:"' + author.affiliation + '"') }}">(<span class="text-muted">{{ author.affiliation }}</span>)</a>
{% endif %}
{% if not loop.last %};
{% endif %}
{% endfor %}
{% endif %}
{% endmacro -%}


{%- macro render_access_rights(record, max=None) %}
{% set label_types = {'open': 'label-success',
'closed': 'label-danger', 
'restricted': 'label-warning', 
'embargoed': 'label-info', 
}
%}
{% if record.access_right %}
<span class="label {{ label_types[record.access_right] }}">{{ record.access_right }}</span>
{%- if record.access_right is equalto 'embargoed' -%}, 
will be available as <span class="label {{ label_types['open'] }}">open access</span> on {{ record.embargo_date }}
{% endif %}
{% endif %}
{% endmacro -%}


{%- macro render_deposition_type(record, max=None) %}
{% set label_types = {
'software': 'label-success',
'dataset': 'label-danger',
'analysis': 'label-warning',
'dmp': 'label-info',
}
%}
{% if record.upload_type %}
<span class="label {{ label_types[record.upload_type] }}">{{ record.upload_type }}</span>
{% endif %}
{% endmacro -%}


{%- macro open_panel_section (heading, key, collapse=False) %}
<div class="panel panel-default ">
  <div class="panel-heading">
    <a data-toggle="collapse" class="panel-toggle" href="#collapse-{{key}}">
      {{ heading|safe }}
      <span class="pull-right show-on-collapsed">
        <i class="fa fa-chevron-down"></i>
      </span>
      <span class="pull-right hide-on-collapsed">
        <i class="fa fa-chevron-up"></i>
      </span>
    </a>
  </div>
  <div id="collapse-{{key}}" class="panel-collapse collapse {%if not collapse %}in{%endif %}">
    <div class="panel-body">
{% endmacro -%}


{%- macro close_panel_section() %}
</div></div></div>
{% endmacro -%}


{%- macro archive_panel(rec) %}
<div id="archive-confirm-dialog" class="modal fade" tabindex="-1" 
     role="dialog" aria-labelledby="archiveconfirmdialog-Label" aria-hidden="true">
  <div class="modal-dialog">
    <div class="modal-content">
      <div class="modal-header">
        <button type="button" class="close" data-dismiss="modal" aria-label="Close"><span aria-hidden="true">&times;</span></button>
        <h4 class="modal-title" id="archiveconfirmdialog-Label">Archive</h4>
      </div>
      <div class="modal-body">
          <ul><li>Would you like to archive this record?</li>                     
          <li>If you archive it, the record will be safely backed up to tape.</li></ul>
        <div class="alert help-block alert-danger" id="archive-modal-state-title" style="margin-top: 5px; display: none;">
        </div>
      </div>
    
      <div class="modal-footer">
        <button type="button" class="btn btn-default" data-dismiss="modal">Close</button>
        <button type="button" class="btn btn-primary"
                onclick='$.post("{{ url_for('lwdaap_actions.archive_record', recid=rec.recid) }}")
                                .done(function(data) {
                                        if (data.redirect) {
                                           window.location.replace(data.redirect);
                                        } else {
                                          $("#archive-confirm-dialog").modal("hide")
                                        }
                                      })
                                .fail(function(jqXHR) {
                                        var m = jQuery.parseJSON(jqXHR.responseText).msg;
                                        var st = $("#archive-modal-state-title");
                                        st.html("<p>" + m + "</p>");
                                        st.show(); 
                                      });'>
            Archive
        </button>
      </div>
    </div>
  </div>
</div>
{% endmacro -%}


{%- macro label(tag, content, tbgc="#5D5D5D", cbgc="cadetblue") %}
<div class="pidbadge">
    {% if tag %}
    <span class="tag" style="background-color: {{tbgc}};">
        {{tag|safe}}
    </span>
    {% endif %}
    <span class="content" style="background-color: {{cbgc}};">
        {{content|safe}}
    </span>
</div> 
{% endmacro %}
