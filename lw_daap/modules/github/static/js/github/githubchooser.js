/*
 *
 */
define(function(require) {
    'use strict';

    var $ = require('jquery');

    return require('flight/lib/component')(GithubChooser);

    function GithubChooser() {
        this.attributes({
            useParent: true,
            uploader: '#githubuploader'
        });


        this.after('initialize', function() {
            var that = this;

            this.on('click', function() {
                $.get(that.$node.data('releaseUrl'), function(data) {
                    if (that.attr.useParent) {
                        window.opener.$(that.attr.uploader).trigger('selectedRelease', data);
                        window.close(); 
                    }
                });
            });
        });
    }
});
