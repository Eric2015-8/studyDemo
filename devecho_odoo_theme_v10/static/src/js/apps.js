odoo.define('devecho_odoo_theme_v10.apps', function (require) {
"use strict";

var Apps = require('web.Apps');

Apps.include({
    // Do nothing on update count as needactions have been removed in enterprise
    _on_update_count: function() {},
});

});
