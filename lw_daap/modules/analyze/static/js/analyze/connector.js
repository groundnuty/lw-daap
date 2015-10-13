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
