/*
 * This file is part of Lifewatch DAAP.
 * Copyright (C) 2015 Ana Yaiza Rodriguez Marrero.
 *
 * Lifewatch DAAP is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * Lifewatch DAAP is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Lifewatch DAAP. If not, see <http://www.gnu.org/licenses/>.
 */

define(function(require) {
    'use strict';

    var $ = require('jquery');

    return require('flight/lib/component')(Integrator);

    function Integrator() {
        var that;

        this.attributes({
            unselectedHtml: "Select",
            selectedHtml: '<i class="fa fa-check"></i> Unselect',
            recordsField: '#records',
            integrateField: '#integrate',
            buttonsSelectors: 'a.integrate-chooser',
            paginators: '.pagination a',
            depositButton: '#btn-deposit-analysis'
        });

        this.toggleButton = function(ev) {
            ev.preventDefault();
            $(this).toggleClass('btn-danger');
            $(this).toggleClass('btn-info');
            var selected = $(this).data('selected');
            if (selected) {
                $(this).html(that.attr.unselectedHtml);
            } else {
                $(this).html(that.attr.selectedHtml);
            }
            $(this).data('selected', !selected);
        };

        this.updateFormRecords = function() {
            var c = that.select('recordsField').val();
            if (c == null) {
                c = [];
            }
            var v = $(that.attr.buttonsSelectors).filter(function() {
                return $(this).data('selected');
            }).map(function() {
                return $(this).data('recordId');
            }).get();
            that.select('recordsField').val(c.concat(v));
        };

        this.submitForm = function(ev) {
            that.updateFormRecords();
        };

        this.paginate = function(ev) {
            ev.preventDefault();
            that.$node.attr("action", this.href);
            that.$node.submit();
        }

        this.doDeposit = function(ev) {
            that.select('integrateField').val("yes");
        }

        this.after('initialize', function() {
            that = this;

            $(that.attr.buttonsSelectors).on('click', this.toggleButton);
            this.on('submit', this.submitForm);
            this.select('depositButton').on('click', this.doDeposit);
            $(that.attr.paginators).on('click', this.paginate);
        });
    }
});
