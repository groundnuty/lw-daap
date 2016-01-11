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
            useParent: true,
            modal: '#terminateModal'
        });


        this.after('initialize', function() {
            this.on('click', function() {
                var modal = $(this.attr.modal);
                modal.find('#terminateModal-vm').html(this.$node.data('vmName'));
                modal.find('#terminateModal-form').attr('action', this.$node.data('terminateUrl'));
                modal.modal('toggle');
            });
        });
    }
});
