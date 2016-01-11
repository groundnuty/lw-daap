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

    return require('flight/lib/component')(Flavor);

    function Flavor() {
        this.attributes({
            flavors: {},
            flavor_name: "#flavor_name",
            flavor_vcpus: "#flavor_vcpus",
            flavor_disk: "#flavor_disk",
            flavor_ram: "#flavor_ram"
        });

        this.showFlavors = function(data) {
            $(this.attr.flavor_name).html(data.name);
            $(this.attr.flavor_vcpus).html(data.vcpus);
            $(this.attr.flavor_disk).html(data.disk);
            $(this.attr.flavor_ram).html(data.ram);
        };

        this.after('initialize', function() {
            this.showFlavors(this.attr.flavors[this.$node.val()])

            this.on('change', function() {
                this.showFlavors(this.attr.flavors[this.$node.val()])
            });
            this.on('keyup', function() {
                this.showFlavors(this.attr.flavors[this.$node.val()])
            });
            this.on('keydown', function() {
                this.showFlavors(this.attr.flavors[this.$node.val()])
            });
        });
    }
});
