#!/usr/bin/python

# Plugin by Lukasz Chrzaszcz <l.chrzaszcz@gmail.com>

""" colorize.py - Terminator Plugin to change color of titlebar of individual
terminals """

import os
import sys
import gtk
from terminatorlib.config import Config
import terminatorlib.plugin as plugin
from terminatorlib.translation import _

AVAILABLE = ['Colorize']

class ColorizeConfig:
    new_config = {}
    previous_config = {}

    def __init__(self, previous_config, new_config):
        self.new_config = new_config
        self.previous_config = previous_config

    def __getitem__(self, item):
        return self.get(item)

    def get(self, item):

        if item in self.new_config:
            if 'fg' in item:
                print 'item on list, returning:', item, self.new_config[item]
            return self.new_config[item]
        else:
            return self.previous_config[item]


class Colorize(plugin.MenuItem):
    """ Add custom command to the terminal menu"""
    capabilities = ['terminal_menu']
    config = None
    color_set = None
    ratio = 0.7

    def __init__(self):
        plugin.MenuItem.__init__(self)
        self.config = Config()
        colorize_config = self.config.plugin_get_config(self.__class__.__name__)

        self.color_set = []
        counter = 0
        while colorize_config.get('color' + str(counter)):
            self.color_set.append(colorize_config.get('color' + str(counter)))
            counter += 1

        print self.color_set


    def callback(self, menuitems, menu, terminal):
        """ Add save menu item to log 'content'the menu"""
        vte_terminal = terminal.get_vte()

        change_color_item = gtk.MenuItem(_('Change color'))
        change_color_item.connect("activate", self.change_color, terminal)
        change_color_item.set_has_tooltip(True)
        change_color_item.set_tooltip_text("Change titlebar color of this terminal")

        menuitems.append(change_color_item)

        # sub menu

        pick_color_menu = gtk.Menu()

        counter = 1
        for color in self.color_set:
            color_item = gtk.MenuItem(_('Color') + ' ' + str(counter))
            color_item.connect("activate", self.pick_color, terminal, counter)
            color_item.set_has_tooltip(True)
            color_item.set_tooltip_text("Set this color for current terminal")

            pick_color_menu.append(color_item)
            counter += 1


        item = gtk.MenuItem(_('Pick color'))
        item.set_submenu(pick_color_menu)
        menuitems.append(item)

    def pick_color(self, _widget, Terminal, Index):
        pass

    def change_color(self, _widget, Terminal):
        """ Handle menu item callback by saving text to a file"""
        color_dialog = gtk.ColorSelectionDialog("Pick new terminal's titlebar color")
        color_sel = color_dialog.colorsel

        # set previous colors
        previous_color = gtk.gdk.color_parse(Terminal.config['title_transmit_bg_color'])

        color_sel.set_previous_color(previous_color)
        color_sel.set_current_color(previous_color)
        color_sel.set_has_palette(True)


        response = color_dialog.run()
        if response == gtk.RESPONSE_OK:
            self.set_titlebar_color(Terminal, color_sel.get_current_color())
            # new_transmit_bg_color = color_sel.get_current_color()
            # new_inactive_bg_color = self.get_inactive_color(new_transmit_bg_color)
            #
            #
            # new_transmit_fg_color = self.get_font_color(new_transmit_bg_color)
            # new_inactive_fg_color = self.get_font_color(new_inactive_bg_color)
            #
            # new_color_config = {
            #     'title_transmit_bg_color': new_transmit_bg_color.to_string(),
            #     'title_inactive_bg_color': new_inactive_bg_color.to_string(),
            #     'title_transmit_fg_color': new_transmit_fg_color.to_string(),
            #     'title_inactive_fg_color': new_inactive_fg_color.to_string()
            # }
            #
            # new_config = ColorizeConfig(Terminal.titlebar.config, new_color_config)
            # Terminal.titlebar.config = new_config



            # Terminal.titlebar.config['title_transmit_bg_color'] = color_sel.get_current_color().to_string()
        # response = savedialog.run()
        # if response == gtk.RESPONSE_OK:
        #     try:
        #         # logfile = os.path.join(savedialog.get_current_folder(),
        #         #                        savedialog.get_filename())
        #         fd = open(logfile, 'w+')
        #         # Save log file path,
        #         # associated file descriptor, signal handler id
        #         # and last saved col,row positions respectively.
        #         vte_terminal = Terminal.get_vte()
        #         (col, row) = vte_terminal.get_cursor_position()
        #
        #         self.loggers[vte_terminal] = {"filepath":logfile,
        #                                       "handler_id":0, "fd":fd,
        #                                       "col":col, "row":row}
        #         # Add contents-changed callback
        #         self.loggers[vte_terminal]["handler_id"] = vte_terminal.connect('contents-changed', self.save)
        #     except:
        #         e = sys.exc_info()[1]
        #         error = gtk.MessageDialog(None, gtk.DIALOG_MODAL, gtk.MESSAGE_ERROR,
        #                                   gtk.BUTTONS_OK, e.strerror)
        #         error.run()
        #         error.destroy()

        color_dialog.destroy()


    def get_inactive_color(self, transmit_color):
        return gtk.gdk.Color(transmit_color.red_float * self.ratio,
                      transmit_color.green_float * self.ratio,
                      transmit_color.blue_float * self.ratio)


    def get_font_color(self, bg_color):
        lightness = (((bg_color.red_float * 299) +
                      (bg_color.green_float * 587) +
                      (bg_color.blue_float * 114)) /1000)


        new_fg_color = gtk.gdk.Color(0, 0, 0)

        if lightness < 0.5:
            new_fg_color = gtk.gdk.Color(65535, 65535, 65535)

        return new_fg_color


    def set_titlebar_color(self, Terminal, color):
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

        new_config = ColorizeConfig(Terminal.titlebar.config, new_color_config)
        Terminal.titlebar.config = new_config


