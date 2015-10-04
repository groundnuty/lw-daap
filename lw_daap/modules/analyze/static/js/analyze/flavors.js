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
        });
    }
});
