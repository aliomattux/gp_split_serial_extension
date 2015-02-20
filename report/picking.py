# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-2010 Tiny SPRL (<http://tiny.be>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
from openerp.report import report_sxw

class picking(report_sxw.rml_parse):
    def __init__(self, cr, uid, name, context):
        super(picking, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'time': time,
            'get_product_desc': self.get_product_desc,
            'get_lines': self.get_lines,
        })

    def get_lines(self, picking):
        serial_pool = self.pool.get('serial.move')
        stockserial_pool = self.pool.get('stock.item.serial')
        final_moves = []
        for move in picking.move_lines:
            search_ids = stockserial_pool.search(self.cr, self.uid, [('move_id', '=', move.id)])
            if search_ids:
                serials = stockserial_pool.read(self.cr, self.uid, search_ids, ['pack_id', 'name'])
                for smove in serials:
                    final_moves.append([move, smove['name'] and smove['name'][1] or "", 1])
            else:
                final_moves.append([move, move.prodlot_id and move.prodlot_id.name or "", move.product_qty])
        return final_moves

    def get_product_desc(self, move_line):
        desc = move_line.product_id.name
        if move_line.product_id.default_code:
            desc = '[' + move_line.product_id.default_code + ']' + ' ' + desc
        return desc

for suffix in ['', '.in', '.out']:
    report_sxw.report_sxw('report.stock.picking.serial.list' + suffix,
                          'stock.picking' + suffix,
                          'addons/stock/report/picking.rml',
                          parser=picking)
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
