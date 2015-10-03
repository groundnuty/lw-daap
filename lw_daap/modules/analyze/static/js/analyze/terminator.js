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
