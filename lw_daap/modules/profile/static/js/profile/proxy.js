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
 * proxy management 
 */
define(function(require) {
    'use strict';

    var $ = require('jquery');
     
    var signer = require('js/profile/signer');

    return require('flight/lib/component')(ProxyDelegator);

    function ProxyDelegator() {
       this.attributes({
            delegateBtn: '#delegateButton',
            userDN: '#userDN',
            userCERT: '#userCERT',
            privateKey: '#privateKey',
            requestUrl: 'https://localhost/',
            delegateUrl: 'https://localhost/',  
            removeUrl: 'https://localhost/',
            errorField: '#delegationModalError',
            spinner: '#delegateButtonSpin',
            nextUrl: ''
        }); 

        var that;

        this.updateButtons = function(ev, data) {
            if (data.user_proxy) {
                $('#remove_delegation_button').show();
                $('#delegation_button').hide();
                $('#extend_delegation_button').show();
                $('#proxy-msg').html("Your proxy is valid for " + data.time_left);
                $('#proxy-msg').attr("class", "alert alert-success");
                if ( that.attr.nextUrl != '' ) { window.location=that.attr.nextUrl; }
            } else {
                $('#remove_delegation_button').hide();
                $('#delegation_button').show();
                $('#extend_delegation_button').hide();
                $('#proxy-msg').html("No delegation found");
                $('#proxy-msg').attr("class", "alert alert-warning");
            }
        };

        this.removeDelegation = function() {
            $.post(that.attr.removeUrl)
                .done(function() {
                    that.trigger("proxyUpdate", {user_proxy: false});
                });
        };

        this.doDelegate = function() {
            that.select('spinner').show();
            $.get(that.attr.requestUrl, function(data) {
                var userCERT = that.select('userCERT').val();
                var privateKey = that.select('privateKey').val();
                var x509Proxy = signer(data, privateKey, userCERT);
                x509Proxy += "" + userCERT;

                $.ajax({
                    url : that.attr.delegateUrl,
                    type : "POST",
                    contentType : "text/plain; charset=UTF-8",
                    dataType : 'text',
                    data: x509Proxy,
                    processData : false,
                    beforeSend : function(xhr) {
                        xhr.withCredentials = true;
                    },
                    xhrFields : {
                        withCredentials : true
                    }
                }).done(function(data) {
                    that.$node.modal('hide');
                    var obj_data = $.parseJSON(data);
                    that.trigger('proxyUpdate', obj_data);
                }).fail(function() {
                    that.select('errorField').html("<b>ERROR:</b> Unable to delegate proxy to server");
                    that.select('errorField').show();
                }).always(function() {
                    that.select('spinner').hide();
                });
            }).fail(function () {
                that.select('errorField').html("<b>ERROR:</b> Unable to get the proxy request from server");
                that.select('errorField').show();
                that.select('spinner').hide();
            });
        };

        this.after('initialize', function() {
            that = this;
            this.select('delegateBtn').on('click', this.doDelegate);
            this.on('proxyUpdate', this.updateButtons);
            $('#remove_delegation_button').on('click', this.removeDelegation);
        }); 
    }
});
