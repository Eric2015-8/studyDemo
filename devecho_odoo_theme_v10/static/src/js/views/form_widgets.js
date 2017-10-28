odoo.define('devecho_odoo_theme_v10.form_widgets', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var form_widgets = require('web.form_widgets');

var QWeb = core.qweb;

form_widgets.FieldStatus.include({
    template: undefined,
    className: "o_statusbar_status",
    render_value: function() {
        var self = this;
        var $content = $(QWeb.render("FieldStatus.content." + ((config.device.size_class <= config.device.SIZES.XS)? 'mobile' : 'desktop'), {
            'widget': this, 
            'value_folded': _.find(this.selection.folded, function (i) {
                return i[0] === self.get('value');
            }),
        }));
        this.$el.empty().append($content.get().reverse());
    },
    bind_stage_click: function () {
        this.$el.on('click','button[data-id]',this.on_click_stage);
    },
});

var FieldPhone = form_widgets.FieldEmail.extend({
    prefix: 'tel',
    init: function() {
        this._super.apply(this, arguments);
        this.clickable = config.device.size_class <= config.device.SIZES.XS;
    },
    render_value: function() {
        this._super();
        if(this.clickable) {
            var text = this.$el.text();
            this.$el.html(text.substr(0, text.length/2) + "&shy;" + text.substr(text.length/2)); // To prevent Skype app to find the phone number
        }
    }
});

core.form_widget_registry
    .add('phone', FieldPhone)
    .add('upgrade_boolean', form_widgets.FieldBoolean) // community compatibility
    .add('upgrade_radio', form_widgets.FieldRadio); // community compatibility

});