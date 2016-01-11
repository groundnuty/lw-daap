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

/*
 *
 */
define(function(require) {
    'use strict';

    var $ = require('jquery');

    return require('flight/lib/component')(Terminator);

    function Terminator() {
        this.attributes({
            modal: '#connectorModal',
            modalError: '#connectorModalError',
            modalWait: '#connectorModalWait',
            modalInfo: '#connectorModalInfo'
        });

        var modal;
        var that;

        this.displayResults = function(ev, data) {
            modal.find(this.attr.modalWait).hide();
            if (data.error) {
                modal.find(this.attr.modalError).html(data.msg);
                modal.find(this.attr.modalError).show();
            } else {
                modal.find(this.attr.modalInfo).html(data.msg);
                modal.find(this.attr.modalInfo).show();
            }
        };
        
        this.getConnection = function() {
            $.get(this.$node.data('connectUrl'))
                .done(function(data) {
                    that.trigger('displayResults', data);
                })
                .fail(function(data) {
                    that.trigger('displayResults', data);
                });
        };

        this.after('initialize', function() {
            that = this;
            modal = $(this.attr.modal);

            modal.on('show.bs.modal', function() {
                modal.find(that.attr.modalWait).show();
                modal.find(that.attr.modalInfo).hide();
                modal.find(that.attr.modalError).hide();
            });

            this.on('displayResults', this.displayResults);

            this.on('click', function() {
                modal.modal('toggle');
                this.getConnection();
            });
        });
    }
});
