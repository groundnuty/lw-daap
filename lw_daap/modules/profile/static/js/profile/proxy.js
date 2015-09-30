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
            removeUrl: 'https://localhost/' 
        }); 

        var that;

        this.updateButtons = function(ev, data) {
            if (data.user_proxy) {
                $('#remove_delegation_button').show()
                $('#delegation_button').hide()
                $('#proxy-msg').html("Your proxy is valid for " + data.time_left)
                $('#proxy-msg').attr("class", "alert alert-success")
            } else {
                $('#remove_delegation_button').hide()
                $('#delegation_button').show()
                $('#proxy-msg').html("No delegation found")
                $('#proxy-msg').attr("class", "alert alert-info")
            }
        };

        this.removeDelegation = function() {
            $.post(that.attr.removeUrl)
                .done(function() {
                    that.trigger("proxyUpdate", {user_proxy: false});
                });
        }

        this.doDelegate = function() {
            $.get(that.attr.requestUrl, function(data) {
                var userCERT = that.select('userCERT').val();
                var privateKey = that.select('privateKey').val();
                var x509Proxy = signer(data.csr, privateKey, userCERT);
                x509Proxy += "" + userCERT;

                $.post(that.attr.delegateUrl, {x509Proxy: x509Proxy})
                    .done(function(data) {
                        that.$node.modal('hide')  
                        that.trigger('proxyUpdate', data);
                    });
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