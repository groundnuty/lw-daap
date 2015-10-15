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
    <a href="../q{{ curate_url }}" class="btn btn-primary ">{{ _('Curate') }}</a>
    {% endif %}
  </div>
  </div>
  <div id="collapse-{{key}}" class="panel-collapse collapse {%if not collapse %}in{%endif %}">
    <div class="panel-body">
{% endmacro -%}

{%- macro close_community_section() %}
</div></div></div>
{% endmacro -%}

