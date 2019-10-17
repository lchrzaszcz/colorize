#!/usr/bin/python

# Plugin by Lukasz Chrzaszcz <l.chrzaszcz@gmail.com>

""" colorize.py - Terminator Plugin to change color of titlebar of individual
terminals """
from gi.repository import GObject

import os
import sys
from terminatorlib.util import dbg
from terminatorlib.config import Config
from gi.repository import Gtk, Gdk
import terminatorlib.plugin as plugin
from terminatorlib.translation import _
from terminatorlib.terminator import Terminator
from terminatorlib.terminal import Terminal
from terminatorlib.container import Container

AVAILABLE = ['Colorize']


class ColorizeConfig:
    new_config = {}
    previous_config = {}

    def __init__(self, previous_config, new_config):
        self.new_config = new_config
        self.previous_config = previous_config

    def __getitem__(self, item):
        return self.get(item)

    def __getattr__(self, name):
        attr = getattr(self.previous_config, name)
        return attr

    def get(self, item):

        if item in self.new_config:
            return self.new_config[item]
        else:
            return self.previous_config[item]


class Colorize(plugin.MenuItem):
    """ Add custom command to the terminal menu"""
    capabilities = ['terminal_menu']
    config = None
    color_set = None
    ratio = 0.7
    bg_ratio = 0.09

    presets = {
        'color0': {
            'name': ' blue',
            'title_transmit_bg_color': '#0076C9'
        },
        'color1': {
            'name': 'purple',
            'title_transmit_bg_color': '#B20DAC'
        },
        'color2': {
            'name': 'yellow',
            'title_transmit_bg_color': '#EAF12A'
        },
        'color3': {
            'name': 'green',
            'title_transmit_bg_color': '#50B20D'
        },
        'color4': {
            'name': 'cyan',
            'title_transmit_bg_color': '#2DF2C1'
        }
    }

    def __init__(self):
        plugin.MenuItem.__init__(self)
        self.config = Config()
        colorize_config = self.config.plugin_get_config(self.__class__.__name__)
        if not colorize_config:
            colorize_config = self.presets
        self.color_set = []
        counter = 0
        if colorize_config:
            while colorize_config.get('color' + str(counter)):
                self.color_set.append(colorize_config.get('color' + str(counter)))
                counter += 1

        dbg(self.color_set)

    def callback(self, menuitems, menu, terminal):
        """ Add save menu item to the menu"""
        vte_terminal = terminal.get_vte()

        if self.is_terminal_default_bg(terminal):
            change_bgcolor_item = Gtk.MenuItem.new_with_mnemonic(_('Colorize background'))
            change_bgcolor_item.connect("activate", self.colorize_terminal_bg_color, terminal)
            change_bgcolor_item.set_tooltip_text("Change background color of this terminal")
        else:
            change_bgcolor_item = Gtk.MenuItem.new_with_mnemonic(_('Restore background'))
            change_bgcolor_item.connect("activate", self.reset_terminal_bg_color, terminal)
            change_bgcolor_item.set_tooltip_text("Change background color of this terminal back")

        change_bgcolor_item.set_has_tooltip(True)

        menuitems.append(change_bgcolor_item)

        change_color_item = Gtk.MenuItem.new_with_mnemonic(_('Choose color'))
        change_color_item.connect("activate", self.change_color, terminal)
        change_color_item.set_has_tooltip(True)
        change_color_item.set_tooltip_text("Change titlebar color of this terminal")

        menuitems.append(change_color_item)

        # sub menu

        pick_color_menu = Gtk.Menu.new()

        counter = 1
        for color in self.color_set:
            if color.get('name'):
                suffix = color['name']
            else:
                suffix = str(counter)
            color_item = Gtk.MenuItem.new_with_mnemonic(_('Color') + ' ' + suffix)
            color_item.connect("activate", self.pick_color, terminal, counter - 1)
            color_item.set_has_tooltip(True)
            color_item.set_tooltip_text("Set this color for current terminal")

            accel_group = Gtk.AccelGroup.new()

            color_item.add_accelerator("activate", accel_group,
                                       ord(str(counter)), Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SHIFT_MASK,
                                       Gtk.AccelFlags.VISIBLE)

            pick_color_menu.append(color_item)
            counter += 1

        item = Gtk.MenuItem.new_with_mnemonic(_('Pick color'))
        item.set_submenu(pick_color_menu)
        menuitems.append(item)

    def is_terminal_default_bg(self, terminal):
        bg_color = Gdk.RGBA()
        bg_color.parse(terminal.config['background_color'])

        return terminal.bgcolor.equal(bg_color)

    def get_terminal_container(self, terminal, container=None):
        terminator = Terminator()
        if not container:
            for window in terminator.windows:
                owner = self.get_terminal_container(terminal, window)
                if owner:
                    return owner
        else:
            for child in container.get_children():
                if isinstance(child, Terminal) and child == terminal:
                    return container
                if isinstance(child, Container):
                    owner = self.get_terminal_container(terminal, child)
                if owner:
                    return owner

    def register_signals(self, container, terminal):
        container.signals.append({
            'name': 'pick-first-color',
            'flags': GObject.SignalFlags.RUN_LAST,
            'return_type': GObject.GType.NONE,
            'param_types': None
        })

        # container.signals.append({
        #     'name': 'split-vert-clone',
        #     'flags': gobject.SIGNAL_RUN_LAST,
        #     'return_type': gobject.TYPE_NONE,
        #     'param_types': None
        # })

        container.register_signals(terminal)

        container.connect_child(terminal, 'pick-first-color', self.pick_first_color)
        # container.connect_child(terminal, 'split-vert-clone', self.split_vert)

    def pick_first_color(self, terminal):
        self.pick_color(None, terminal, 1)

    def pick_color(self, _widget, terminal, index):
        dbg(['picking color', 'index', index, self.color_set[index]['title_transmit_bg_color']])
        self.set_titlebar_color(terminal, Gdk.Color.parse(self.color_set[index]['title_transmit_bg_color']).color)

    def change_color(self, _widget, terminal):
        """ Handle menu item callback by saving text to a file"""
        color_dialog = Gtk.ColorSelectionDialog("Pick new terminal's titlebar color")
        color_sel = color_dialog.get_color_selection()

        # set previous colors
        previous_color = Gdk.color_parse(terminal.config['title_transmit_bg_color'])

        color_sel.set_previous_color(previous_color)
        color_sel.set_current_color(previous_color)
        color_sel.set_has_palette(True)

        response = color_dialog.run()
        if response == Gtk.ResponseType.OK:
            self.set_titlebar_color(terminal, color_sel.get_current_color())

        color_dialog.destroy()

    def get_inactive_color(self, transmit_color):
        return Gdk.Color(transmit_color.red * self.ratio,
                         transmit_color.green * self.ratio,
                         transmit_color.blue * self.ratio)

    def get_font_color(self, bg_color):
        lightness = (((bg_color.red * 299) +
                      (bg_color.green * 587) +
                      (bg_color.blue * 114)) / 1000)

        new_fg_color = Gdk.Color(0, 0, 0)

        if lightness < 0.5:
            new_fg_color = Gdk.Color(65535, 65535, 65535)

        return new_fg_color

    def set_titlebar_color(self, terminal, color):
        dbg(['setting titlebar color', color])
        new_transmit_bg_color = color
        new_inactive_bg_color = self.get_inactive_color(new_transmit_bg_color)

        new_transmit_fg_color = self.get_font_color(new_transmit_bg_color)
        new_inactive_fg_color = self.get_font_color(new_inactive_bg_color)

        new_color_config = {
            'title_transmit_bg_color': new_transmit_bg_color.to_string(),
            'title_inactive_bg_color': new_inactive_bg_color.to_string(),
            'title_transmit_fg_color': new_transmit_fg_color.to_string(),
            'title_inactive_fg_color': new_inactive_fg_color.to_string()
        }

        new_config = ColorizeConfig(terminal.titlebar.config, new_color_config)
        terminal.titlebar.config = new_config

        if not self.is_terminal_default_bg(terminal):
            self.colorize_terminal_bg_color(None, terminal)

    def colorize_terminal_bg_color(self, _widget, terminal):
        bg_color = Gdk.RGBA()
        bg_color.parse(terminal.titlebar.config['title_transmit_bg_color'])

        bg_color.red *= self.bg_ratio
        bg_color.green *= self.bg_ratio
        bg_color.blue *= self.bg_ratio

        terminal.bgcolor = bg_color

    def reset_terminal_bg_color(self, _widget, terminal):
        bg_color = Gdk.RGBA()
        bg_color.parse(terminal.config['background_color'])

        terminal.bgcolor = bg_color
