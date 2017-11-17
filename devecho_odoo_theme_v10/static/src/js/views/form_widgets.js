odoo.define('devecho_odoo_theme_v10.form_widgets', function (require) {
"use strict";

var config = require('web.config');
var core = require('web.core');
var form_widgets = require('web.form_widgets');
var common = require('web.form_common');
var formats = require('web.formats');

var QWeb = core.qweb;

var FieldNumber = common.AbstractField.extend(common.ReinitializeFieldMixin, {
    template: 'FieldNumber',
    events: {
        'change': 'store_dom_value',
    },
    init: function (field_manager, node) {
        this._super(field_manager, node);
        this.password = this.node.attrs.password === 'True' || this.node.attrs.password === '1';
    },
    initialize_content: function () {
        if (!this.get('effective_readonly') && !this.$input) {
            this.$input = this.$el;
        }
        this.setupFocus(this.$el);
    },
    destroy_content: function () {
        this.$input = undefined;
    },
    store_dom_value: function () {
        if (this.$input && this.is_syntax_valid()) {
            this.internal_set_value(this.parse_value(this.$input.val()));
        }
    },
    commit_value: function () {
        this.store_dom_value();
        return this._super();
    },
    render_value: function () {
        var show_value = this.format_value(this.get('value'), '');
        if (this.$input) {
            this.$input.val(show_value);
        } else {
            if (this.password) {
                show_value = new Array(show_value.length + 1).join('*');
            }
            this.$el.text(show_value);
        }
    },
    is_syntax_valid: function () {
        if (this.$input) {
            try {
                this.parse_value(this.$input.val(), '');
            } catch (e) {
                return false;
            }
        }
        return true;
    },
    parse_value: function (val, def) {
        return formats.parse_value(val, this, def);
    },
    format_value: function (val, def) {
        return formats.format_value(val, this, def);
    },
    is_false: function () {
        return this.get('value') === '' || this._super();
    },
    focus: function () {
        if (this.$input) {
            return this.$input.focus();
        }
        return false;
    },
});

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
    .add('number', FieldNumber)
    .add('phone', FieldPhone)
    .add('upgrade_boolean', form_widgets.FieldBoolean) // community compatibility
    .add('upgrade_radio', form_widgets.FieldRadio); // community compatibility

});