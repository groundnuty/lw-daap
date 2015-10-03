#
# (c) 2015 aeonium. 
#

{%- macro open_community_section (heading, view_url, curate_url, key, collapse=False) %}
<div class="panel panel-deposit ">
  <div class="panel-heading">
    <a data-toggle="collapse" class="panel-toggle" href="#collapse-{{key}}">
      <span class="show-on-collapsed pull-left">
        <i class="fa fa-chevron-down"></i>
      </span>
      <span class="hide-on-collapsed pull-left">
        <i class="fa fa-chevron-up"></i>
      </span>
      {{ heading }}
    </a>
    <div class="pull-right">
    <a href="{{ view_url }}" class="btn btn-danger ">{{ _('View') }}</a>
    {% if curate_url %}
    <a href="{{ curate_url }}" class="btn btn-primary ">{{ _('Curate') }}</a>
    {% endif %}
  </div>
  </div>
  <div id="collapse-{{key}}" class="panel-collapse collapse {%if not collapse %}in{%endif %}">
    <div class="panel-body">
{% endmacro -%}

{%- macro close_community_section() %}
</div></div></div>
{% endmacro -%}

