#!/usr/bin/python
# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from PyQt5.QtGui import QColor
from PyQt5.QtCore import QRect
from src.utils import log_method_name

POS_FIX_NORMAL = [165, 18, 52.6, 5, 5]
POS_FIX_QUAD = [163, 19, 26.3, 2, 2]

ALPHA = 255

RECT_COLOR = {

    'UltraRare': [255, 255, 255, ALPHA],   # White
    'HighValuable': [255, 0, 0, ALPHA],  # Brown
    'Valuable': [175, 85, 20, ALPHA],      # Yellow
    'MidValuable': [255, 255, 0, ALPHA],     # Green
    'LowValuable': [0, 225, 0, ALPHA]
}


class RectProcess(object):
    """ GUI class """

    def __init__(self, width_scale, height_scale):
        log_method_name()
        self.width_scale = width_scale
        self.height_scale = height_scale
        self.shift = None
        self.border_size = None
        self.stash_type = None
        self.heigh_fix = None
        self.width_fix = None
        self.size_fix = None
        self.items = None
        self.size_modifier = None
        self.rect_color = None
        self.rectangles = []
        self.qp = None
        POS_FIX_NORMAL[0] *= height_scale
        POS_FIX_QUAD[0] *= height_scale
        POS_FIX_NORMAL[1] *= width_scale
        POS_FIX_QUAD[1] *= width_scale
        POS_FIX_NORMAL[2] *= (height_scale + width_scale) / 2
        POS_FIX_QUAD[2] *= (height_scale + width_scale)/2
        POS_FIX_NORMAL[3] *= (height_scale + width_scale) / 2
        POS_FIX_QUAD[3] *= (height_scale + width_scale) / 2

    def get_rectangles(self):
        log_method_name()
        return self.rectangles

    def define_rects(self, items, stash_type):
        log_method_name()

        self.rectangles = {
            'UltraRare': [],
            'HighValuable': [],
            'Valuable': [],
            'MidValuable': [],
            'LowValuable': []
        }
        self.items = items

        if 'Normal' == stash_type:
            self.heigh_fix, self.width_fix, self.size_modifier, self.shift, self.border_size = POS_FIX_NORMAL
        else:
            self.heigh_fix, self.width_fix, self.size_modifier, self.shift, self.border_size = POS_FIX_QUAD

        for item in self.items:
            self.rect_color = RectColor(item)
            rect_x = item.x*self.size_modifier+self.width_fix
            rect_y = item.y*self.size_modifier+self.heigh_fix
            rect_w = (item.width*self.size_modifier) - self.shift
            rect_h = (item.height*self.size_modifier) - self.shift
            self.rectangles[self.rect_color.status].append([QRect(rect_x, rect_y, rect_w, rect_h), self.rect_color, item])  # size




class RectColor(QColor):

    def __init__(self, item):
        log_method_name()
        super(QColor, self).__init__()
        self.item_score = 0
        self.r = 0
        self.g = 0
        self.b = 0
        self.a = 0
        self.item = item
        # self.calculate_score()
        self.set_colors()

    def check_tiers(self):
        log_method_name()
        rect_color = None
        if self.item.score <= 200:
            rect_color = RECT_COLOR['LowValuable']
            self.status = 'LowValuable'
        if self.item.score > 200:
            rect_color = RECT_COLOR['MidValuable']
            self.status = 'MidValuable'
        if self.item.score > 280:
            rect_color = RECT_COLOR['Valuable']
            self.status = 'Valuable'
        if self.item.score > 350:
            rect_color = RECT_COLOR['HighValuable']
            self.status = 'HighValuable'
        if self.item.score > 480:
            rect_color = RECT_COLOR['UltraRare']
            self.status = 'UltraRare'

        # if self.item_score < :
        #     rect_color = RECT_COLOR['Unknown']

        return rect_color

    def set_colors(self):
        log_method_name()
        r, g, b, a = self.check_tiers()
        self.setRed(r)
        self.setGreen(g)
        self.setBlue(b)
        self.setAlpha(a)





