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
 * This file is part of Invenio.
 * Copyright (C) 2014 CERN.
 *
 * Invenio is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License as
 * published by the Free Software Foundation; either version 2 of the
 * License, or (at your option) any later version.
 *
 * Invenio is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with Invenio; if not, write to the Free Software Foundation, Inc.,
 * 59 Temple Place, Suite 330, Boston, MA 02111-1307, USA.
 */
define(function(require) {
    'use strict';

    var withUtil = require('js/instruments/uploader/mixins/util'),
        $ = require('jquery');

    return require('flight/lib/component')(GithubUploader, withUtil);

    function GithubUploader() {
        this.attributes({
            upload_url: "http://httpbin.org/post",
            github_chooser_url: "http://httpbin.org/",
            width: 640,
            height: 552
        });

        var self;
        
        var github_files = {};

        this.after('initialize', function() {
            self = this; 

            this.on('click', function() {
                var left = (window.screenX || window.screenLeft) +
                           ((window.outerWidth || document.documentElement.offsetWidth) - self.attr.width) / 2,
                    top = (window.screenY || window.screenTop) +
                          ((window.outerHeight || document.documentElement.offsetHeight) - self.attr.height) / 2;
                var features = "width=" + self.attr.width + ",height=" + self.attr.height +  ",left=" + left +
                              ",top=" + top + ",scrollbars=yes";
                var w = window.open(self.attr.github_chooser_url, 'GitHub_Uploader_Chooser', features);
                w.focus();
            });

            this.on('selectedRelease', function(ev, data) {
                var new_files = {}
                name = data.owner + "-" + data.repo + "-" + data.name; 
                if (github_files[name] === undefined) {
                    github_files[name] = data
                    github_files[name].id = self.guid(); 
                    github_files[name].status = 1;
                    github_files[name].percent = 0;
                    github_files[name].name = name;
                    
                    new_files[name] = github_files[name];
                } else {
                        self.trigger('uploaderError', {
                            message: "Duplicated File"
                        });
                }

                var files = $.map(new_files, function(file) {
                    return {
                        id: file.id,
                        name: file.name,
                        percent: file.percent,
                        status: file.status
                    }
                });

                self.trigger('filesAdded', {
                    files: files 
                });
            });

            this.on('uploadFiles', function(ev, data) {
                $.each(github_files, function(key, val) {
                    var filename = val.name;
                    var all_done = true;
                    if (val.status !== 5) {
                        self.trigger('fileProgressUpdated', {
                            upload_speed: '',
                            file: {
                                id: val.id,
                                percent: 80,
                                name: val.name
                            }
                        });
                        var desc = $('#file-desc-' + val.id).val();
                        $.ajax({
                            type: 'POST',
                            url: self.attr.upload_url,
                            data: $.param({
                                name: val.name,
                                url: val.url,
                                description: desc
                            }),
                            dataType: "json"
                        }).done(function(data) {
                            github_files[filename].server_id = data.id;
                            github_files[filename].status = 5;
                            github_files[filename].percent = 100;
                            self.trigger('fileProgressUpdated', {
                                upload_speed: '',
                                file: github_files[filename] 
                            });
                            self.trigger('fileUploadedCompleted', {
                                file: github_files[filename]
                            });

                            self.trigger('filesUploadCompleted', {
                                files: github_files 
                            });
                        });
                    }
                });
            });

            this.on('stopUploadFiles', function(ev, data) {});

            this.on('fileRemoved', function(ev, data) {
                var fileName;
                $.each(github_files, function(key, val) {
                    if (val.id === data.fileId) {
                        fileName = key;
                    }
                });
                delete github_files[fileName];
            });
        });

    }
/*
    {
        this.attributes({
            dropbox_url: "http://httpbin.org/post",
            preupload_hooks: {}
        });

        var self;
        var pause = false;

        var dropboxFiles = {};

        var options = {

            success: function(files) {
                var newFiles = {};
                files.forEach(function(file) {
                    if (dropboxFiles[file.name] === undefined) {
                        dropboxFiles[file.name] = file;
                        dropboxFiles[file.name].id = self.guid();
                        dropboxFiles[file.name].status = 1;
                        dropboxFiles[file.name].percent = 0;

                        newFiles[file.name] = dropboxFiles[file.name]
                    } else {
                        self.trigger('uploaderError', {
                            message: "Duplicated File"
                        });
                    }
                });
                files = $.map(newFiles, function(file) {
                    return {
                        id: file.id,
                        name: file.name,
                        size: self.bytesToSize(file.bytes),
                        percent: file.percent,
                        status: file.status
                    }
                });
                if (files.length > 0) {
                    self.trigger('filesAdded', {
                        files: files
                    });
                }
            },

            cancel: function() {
                console.log('canceled');
            },

            linkType: "direct", // "preview" or "direct"

            multiselect: true,

            // extensions: ['.pdf', '.doc', '.docx'],
        };

        //
        // Evevt Handlers
        //

        this.after('initialize', function() {
            self = this;

            this.on('click', function() {
                Dropbox.choose(options);
            });

            this.on('uploadFiles', function(ev, data) {
                for (var key in self.attr.preupload_hooks) {
                    if (self.attr.preupload_hooks.hasOwnProperty(key)) self.attr.preupload_hooks[key](self);
                }
                pause = false;

                $.each(dropboxFiles, function(key, val) {
                    var filename = val.name;
                    var all_done = true;
                    if (val.status !== 5) {
                        if (pause === 5) return false;
                        self.trigger('fileProgressUpdated', {
                            upload_speed: '',
                            file: {
                                id: val.id,
                                percent: 80,
                                name: val.name
                            }
                        });
                        var desc = $('#file-desc-' + val.id).val();
                        $.ajax({
                            type: 'POST',
                            url: self.attr.dropbox_url,
                            data: $.param({
                                name: val.name,
                                size: val.bytes,
                                url: val.link,
                                description: desc
                            }),
                            dataType: "json"
                        }).done(function(data) {
                            dropboxFiles[filename].server_id = data.id;
                            dropboxFiles[filename].status = 5;
                            dropboxFiles[filename].percent = 100;
                            self.trigger('fileProgressUpdated', {
                                upload_speed: '',
                                file: dropboxFiles[filename] 
                            });
                            self.trigger('fileUploadedCompleted', {
                                file: dropboxFiles[filename]
                            });

                            all_done = true;
                            $.each(dropboxFiles, function(key, val) {
                                if (val.status !== 5) all_done = false;
                            });
                            if (all_done) {
                                self.trigger('filesUploadCompleted', {
                                    files: dropboxFiles
                                });
                            }
                        });
                    }
                });

            });

            this.on('stopUploadFiles', function(ev, data) {});

            this.on('fileRemoved', function(ev, data) {
                var fileName;
                $.each(dropboxFiles, function(key, val) {
                    if (val.id === data.fileId) {
                        fileName = key;
                    }
                });
                delete dropboxFiles[fileName];
            });
        });
    }
    */
});
