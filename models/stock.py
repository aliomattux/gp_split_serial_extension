# -*- coding: utf-8 -*-
##############################################################################
# Module by Kranbery Techonolgies LLC
##############################################################################

from openerp.osv import osv, fields, orm
from openerp import SUPERUSER_ID, api
#from openerp import netsvc
import collections
import openerp.addons.decimal_precision as dp
import time
import logging



_logger = logging.getLogger(__name__)

class StockMove(osv.osv):
    _inherit = 'stock.move'
    _columns = {
        'prod_lot_id': fields.many2one('stock.production.lot', 'Serial Number', domain="[('product_id','=',product_id)]"),
    }


class stock_move_serial(osv.osv):
    _name="stock.move"
    _inherit="stock.move"
    
    def action_scrap(self, cr, uid, ids, quantity, location_id, restrict_lot_id=False, restrict_partner_id=False, context=None):
	res = super(stock_move_serial, self).action_scrap(cr, uid, ids, quantity, locaton_id, restrict_lot_id, restrict_partner_id, context)

        # Get Serial Numbers
        stock_item_serial = self.pool.get('stock.item.serial')
        stock_item_serial_ids = stock_item_serial.search(cr, uid, [('move_id','=', context.get('active_id')), ('scrapped','=',context.get('scrap'))])
        stock_picking_serial = self.pool.get('stock.picking')  
        stock_picking_serial.serial_move_history(cr, SUPERUSER_ID, ids, stock_item_serial_ids, context) 

	return res

 
class stock_move_scrap_serial(osv.osv_memory):
    _inherit = "stock.move.scrap"
    #_description = "Scrap Products"
    #_inherit = "stock.move.consume"

    
    def default_get(self, cr, uid, fields, context=None):
        res = super(stock_move_scrap_serial, self).default_get(cr, uid, fields, context)
        if context.get('scrapped_product_qty'):       
            res.update({'product_qty': context.get('scrapped_product_qty')})
        return res
        
        

    def action_product_serial_number(self, cr, uid, ids, context={}):
                       
        context['parent_init_ids'] = ids                       
        for msnw in self.browse(cr, uid, ids): 
            context['scrapped_product_qty'] = msnw.product_qty
                               
                               
        return {
        'name':("Serial Numbers"),
        'view_mode': 'form',
        'view_id': False,
        'view_type': 'form',
        'res_model': 'product.serial.number.wizard',
        'type': 'ir.actions.act_window',
        'nodestroy': False,
        'target': 'new',
        'domain': '[]',
        'context': context,                
                                        
        } 


class stock_picking_serial(osv.osv):
    _inherit  = "stock.picking"
#---------------------------------------------------------
#  General Procurement / Kranbery - convert to inheritance version
#---------------------------------------------------------
    @api.cr_uid_ids_context
    def do_transfer(self, cr, uid, picking_ids, context=None):
	print 'CALL'
        res = super(stock_picking_serial, self).do_transfer(cr, uid, picking_ids, context=context)
        picking_obj = self.pool.get('stock.picking')
	for picking in picking_obj.browse(cr, uid, picking_ids):
	    if picking.state == 'done':
		for move in picking.move_lines:
		    if move.state == 'done':
			self.serial_move_history(cr, SUPERUSER_ID, picking_ids, move, context)

         
    # Stock split modified from warehouse stock split to work with parsed scanned text area
    def serial_move_history(self, cr, uid, ids, move_obj, context=None):
        if context is None:
            context = {}  

        # Get Serial Numbers
        stock_item_serial = self.pool.get('stock.item.serial')
        
        # Handle scrapped situation
        scrapped = False
        if context.get('scrap'):
            scrapped = context.get('scrap')
        if scrapped:
            stock_item_serial_ids = move_obj
        else:            
            stock_item_serial_ids = stock_item_serial.search(cr, uid, [('move_id','=',move_obj.id)])
            
        #  Get associated serial numbers    
        serial_numbers = stock_item_serial.browse(cr, uid, stock_item_serial_ids)

        
        # Process Serial Numbers and record history in serial move
        if serial_numbers:
            
            # Get move data
            stock_move = self.pool.get('stock.move')
            move_obj = stock_move.browse(cr, uid, context.get('active_id'))   
                        
            for serial_lines in serial_numbers:
            

                self.pool.get('serial.move').create_rapid_insert(cr, uid, {
			'serial_number':serial_lines.name.id,
			'move_id':move_obj.id,
			'name':move_obj.name,
			'pack_id':serial_lines.pack_id.strip(),
			'mfg_product_code':serial_lines.mfg_product_code,
			'priority':move_obj.priority,
			'create_sn_date':move_obj.create_date,
			'date': time.strftime('%Y-%m-%d %H:%M:%S'),
			'date_expected':move_obj.date_expected,
			'product_id':move_obj.product_id.id,
			'product_qty':move_obj.product_qty,
			'product_uom':move_obj.product_uom.id,
			'product_uos_qty':move_obj.product_uos_qty,
			'product_uos':move_obj.product_uos.id,
			'product_packaging':move_obj.product_packaging.id,
			'location_id':move_obj.location_id.id,
			'location_dest_id':move_obj.location_dest_id.id,
			'partner_id':move_obj.partner_id.id,
			'prod_lot_id':move_obj.prod_lot_id.id,
	#		'auto_validate':move_obj.auto_validate,
			'move_dest_id':move_obj.move_dest_id.id,
			'picking_id':move_obj.picking_id.id,
			'note':move_obj.note,
			'state':move_obj.state,
			'price_unit':move_obj.price_unit,
	#		'price_currency_id':move_obj.price_currency_id.id,
			'company_id':move_obj.company_id.id,
			'backorder_id':move_obj.backorder_id.id,
			'origin':move_obj.origin,
			'scrapped': scrapped,
		#	'type':move_obj.type,
			'picking_type_id': move_obj.picking_type_id.id,


},
        context=context)    
        
        # remove from scrapped list
        if scrapped:
            stock_item_serial_ids = stock_item_serial.search(cr, uid, [('move_id','=',context.get('active_id')),('scrapped','=',scrapped)])
            stock_item_serial.unlink(cr, uid, stock_item_serial_ids, context=None)
                                                
        return True   
      


class stock_item_serial(osv.Model):
    """Serial Number Related to Stock Move"""
    _name = 'stock.item.serial'
    _description = 'Product Serial Number'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id, line.name))
        return res

    #def create(self, cr, uid, vals, context=None):
    #    return super(stock_item_serial, self).create(cr, uid, vals, context)

    _columns = {
        'date': fields.datetime('Creation Date'),
        'name': fields.many2one('item.serial', 'Serial Number', required=True), 
        'mfg_product_code': fields.char('Manufacture Product Code', size=128, required=False),        
        'move_id': fields.many2one('stock.move', 'Related Move'),
        'scrapped': fields.boolean('Scrapped'),
        'committed': fields.boolean('Serial number committed'),
        
        # Pack manipulation and tracking
        'pack_id': fields.char('Pack Number', size=128, required=True),        
    }
    
    _defaults = {
        'committed': False,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'scrapped':False,
        
    }  

stock_item_serial()


class stock_item_pack(osv.Model):
    """Packs Related to item"""
    _name = 'stock.item.pack'
    _rec_name = 'name'        
    _description = 'Pack Numbers'

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for line in self.browse(cr, uid, ids, context=context):
            res.append((line.id, line.name))
        return res

    #def create(self, cr, uid, vals, context=None):
    #    return super(stock_item_serial, self).create(cr, uid, vals, context)

    _columns = {
        'date': fields.datetime('Creation Date'),
        'name': fields.char('Pack ID', size=256, required=True, readonly=True), 
        'mfg_product_code': fields.char('Manufacture Product Code', size=128, required=False),          
        'qty': fields.float('Pack QTY', readonly=False, required=False, help='Qty of Lot'), 
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True, domain=[('type','<>','service')],states={'done': [('readonly', True)]}),

    }
    
    _defaults = {
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }  



class item_serial(osv.Model):
    """Item Serial Numbers Mass Table Storage - Records a list of all serial numbers created"""
    _name = 'item.serial'
    _description = 'Item Serial Number'

    _columns = {
        'date': fields.datetime('Creation Date'),
        'name': fields.char('Serial Number', size=128, required=True),
        'created_move_id': fields.many2one('stock.move', 'Created on Move'),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True, domain=[('type','<>','service')],states={'done': [('readonly', True)]}),
        'committed': fields.boolean('Serial number committed'),
    }
    
    _defaults = {
        'committed': False,
        'date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
    }  


class serial_move(osv.osv):

    """ serial move which is the stock move data but for non-dependent logging of serial number activity """

    _name = 'serial.move'
    _rec_name = 'serial_number'

    _columns = {
        'serial_number': fields.many2one('item.serial', 'Serial Number', required=True),
        'pack_id': fields.char('Pack Number', size=256),
        'mfg_product_code': fields.char('Manufacture Product Code', size=128, required=False),         
        'move_id': fields.many2one('stock.move', 'Related Move'),
        'name': fields.char('Description', required=True, select=True),
        'priority': fields.selection([('0', 'Not urgent'), ('1', 'Urgent')], 'Priority'),
        'create_sn_date': fields.datetime('Creation Date', required=True, select=True, help="Creation Date"),
        'date': fields.datetime('Date', required=True, select=True, help="Move date: scheduled date until move is done, then date of actual move processing", states={'done': [('readonly', True)]}),
        'date_expected': fields.datetime('Scheduled Date', states={'done': [('readonly', True)]},required=True, select=True, help="Scheduled date for the processing of this move"),
        'product_id': fields.many2one('product.product', 'Product', required=True, select=True, domain=[('type','<>','service')],states={'done': [('readonly', True)]}),

        'product_qty': fields.float('Quantity', digits_compute=dp.get_precision('Product Unit of Measure'),
            required=True,states={'done': [('readonly', True)]},
            help="This is the quantity of products from an inventory "
                "point of view. For moves in the state 'done', this is the "
                "quantity of products that were actually moved. For other "
                "moves, this is the quantity of product that is planned to "
                "be moved. Lowering this quantity does not generate a "
                "backorder. Changing this quantity on assigned moves affects "
                "the product reservation, and should be done with care."
        ),
        'product_uom': fields.many2one('product.uom', 'Unit of Measure', required=False,states={'done': [('readonly', True)]}),
        'product_uos_qty': fields.float('Quantity (UOS)', digits_compute=dp.get_precision('Product Unit of Measure'), states={'done': [('readonly', True)]}),
        'product_uos': fields.many2one('product.uom', 'Product UOS', states={'done': [('readonly', True)]}),
        'product_packaging': fields.many2one('product.packaging', 'Packaging', help="It specifies attributes of packaging like type, quantity of packaging,etc."),

        'location_id': fields.many2one('stock.location', 'Source Location', required=False, select=True,states={'done': [('readonly', True)]}, help="Sets a location if you produce at a fixed location. This can be a partner location if you subcontract the manufacturing operations."),
        'location_dest_id': fields.many2one('stock.location', 'Destination Location', required=False,states={'done': [('readonly', True)]}, select=True, help="Location where the system will stock the finished products."),
        'partner_id': fields.many2one('res.partner', 'Destination Address ', states={'done': [('readonly', True)]}, help="Optional address where goods are to be delivered, specifically used for allotment"),
        
        # Old Serial Number
        'prod_lot_id': fields.many2one('stock.production.lot', '', states={'done': [('readonly', True)]}, help="Serial number is used to put a serial number on the production", select=True),

        'auto_validate': fields.boolean('Auto Validate'),

        'move_dest_id': fields.many2one('stock.move', 'Destination Move', help="Optional: next stock move when chaining them", select=True),
        'picking_id': fields.many2one('stock.picking', 'Reference', select=True,states={'done': [('readonly', True)]}),
        'note': fields.text('Notes'),
        'state': fields.selection([('draft', 'New'),
                                   ('cancel', 'Cancelled'),
                                   ('waiting', 'Waiting Another Move'),
                                   ('confirmed', 'Waiting Availability'),
                                   ('assigned', 'Available'),
                                   ('done', 'Done'),
                                   ], 'Status', readonly=True, select=True,
                 help= "* New: When the stock move is created and not yet confirmed.\n"\
                       "* Waiting Another Move: This state can be seen when a move is waiting for another one, for example in a chained flow.\n"\
                       "* Waiting Availability: This state is reached when the procurement resolution is not straight forward. It may need the scheduler to run, a component to me manufactured...\n"\
                       "* Available: When products are reserved, it is set to \'Available\'.\n"\
                       "* Done: When the shipment is processed, the state is \'Done\'."),
        'price_unit': fields.float('Unit Price', digits_compute= dp.get_precision('Product Price'), help="Technical field used to record the product cost set by the user during a picking confirmation (when average price costing method is used)"),
       # 'price_currency_id': fields.many2one('res.currency', 'Currency for average price', help="Technical field used to record the currency chosen by the user during a picking confirmation (when average price costing method is used)"),
        'company_id': fields.many2one('res.company', 'Company', required=False, select=True),
        'scrapped': fields.boolean('Scrapped', readonly=True),
        'backorder_id': fields.related('picking_id','backorder_id',type='many2one', relation="stock.picking", string="Back Order of", select=True),
        'origin': fields.related('picking_id','origin',type='char', size=64, relation="stock.picking", string="Source", store=True),
	'picking_type_id': fields.many2one('stock.picking.type', 'Picking Type'),
     #   'type': fields.related('picking_id', 'type', type='selection', selection=[('out', 'Shipping'), ('in', 'Receiving'), ('internal', 'Internal Move')], string='Shipping Type'),
    }


    # ORM optmization
    def create_rapid_insert(self, cr, user, vals, context=None):
        """
        Create a new record for the model.

        The values for the new record are initialized using the ``vals``
        argument, and if necessary the result of ``default_get()``.

        :param cr: database cursor
        :param user: current user id
        :type user: integer
        :param vals: field values for new record, e.g {'field_name': field_value, ...}
        :type vals: dictionary
        :param context: optional context arguments, e.g. {'lang': 'en_us', 'tz': 'UTC', ...}
        :type context: dictionary
        :return: id of new record created
        :raise AccessError: * if user has no create rights on the requested object
                            * if user tries to bypass access rules for create on the requested object
        :raise ValidateError: if user tries to enter invalid value for a field that is not in selection
        :raise UserError: if a loop would be created in a hierarchy of objects a result of the operation (such as setting an object as its own parent)

        **Note**: The type of field values to pass in ``vals`` for relationship fields is specific.
        Please see the description of the :py:meth:`~osv.osv.osv.write` method for details about the possible values and how
        to specify them.

        """
        if not context:
            context = {}

        if self.is_transient():
            self._transient_vacuum(cr, user)

        self.check_access_rights(cr, user, 'create')

#        if self._log_access:
 #           for f in osv.orm.LOG_ACCESS_COLUMNS:
  #              if vals.pop(f, None) is not None:
   #                 _logger.warning(
    #                    'Field `%s` is not allowed when creating the model `%s`.',
     #                   f, self._name)
        vals = self._add_missing_default_values(cr, user, vals, context)

        tocreate = {}
        for v in self._inherits:
            if self._inherits[v] not in vals:
                tocreate[v] = {}
            else:
                tocreate[v] = {'id': vals[self._inherits[v]]}
        (upd0, upd1, upd2) = ('', '', [])
        upd_todo = []
        unknown_fields = []
        for v in vals.keys():
            if v in self._inherit_fields and v not in self._columns:
                (table, col, col_detail, original_parent) = self._inherit_fields[v]
                tocreate[table][v] = vals[v]
                del vals[v]
            else:
                if (v not in self._inherit_fields) and (v not in self._columns):
                    del vals[v]
                    unknown_fields.append(v)
        if unknown_fields:
            _logger.warning(
                'No such field(s) in model %s: %s.',
                self._name, ', '.join(unknown_fields))

        # Try-except added to filter the creation of those records whose filds are readonly.
        # Example : any dashboard which has all the fields readonly.(due to Views(database views))
        try:
            cr.execute("SELECT nextval('"+self._sequence+"')")
        except:
            raise osv.orm.except_orm(_('UserError'),
                _('You cannot perform this operation. New Record Creation is not allowed for this object as this object is for reporting purpose.'))

        id_new = cr.fetchone()[0]
        for table in tocreate:
            if self._inherits[table] in vals:
                del vals[self._inherits[table]]

            record_id = tocreate[table].pop('id', None)
            
            # When linking/creating parent records, force context without 'no_store_function' key that
            # defers stored functions computing, as these won't be computed in batch at the end of create(). 
            parent_context = dict(context)
            parent_context.pop('no_store_function', None)
            
            if record_id is None or not record_id:
                record_id = self.pool.get(table).create(cr, user, tocreate[table], context=parent_context)
            else:
                self.pool.get(table).write(cr, user, [record_id], tocreate[table], context=parent_context)

            upd0 += ',' + self._inherits[table]
            upd1 += ',%s'
            upd2.append(record_id)

        #Start : Set bool fields to be False if they are not touched(to make search more powerful)
        bool_fields = [x for x in self._columns.keys() if self._columns[x]._type=='boolean']

        for bool_field in bool_fields:
            if bool_field not in vals:
                vals[bool_field] = False
        #End
        for field in vals.copy():
            fobj = None
            if field in self._columns:
                fobj = self._columns[field]
            else:
                fobj = self._inherit_fields[field][2]
            if not fobj:
                continue
            groups = fobj.write
            if groups:
                edit = False
                for group in groups:
                    module = group.split(".")[0]
                    grp = group.split(".")[1]
                    cr.execute("select count(*) from res_groups_users_rel where gid IN (select res_id from ir_model_data where name='%s' and module='%s' and model='%s') and uid=%s" % \
                               (grp, module, 'res.groups', user))
                    readonly = cr.fetchall()
                    if readonly[0][0] >= 1:
                        edit = True
                        break
                    elif readonly[0][0] == 0:
                        edit = False
                    else:
                        edit = False

                if not edit:
                    vals.pop(field)
        for field in vals:
            if self._columns[field]._classic_write:
                upd0 = upd0 + ',"' + field + '"'
                upd1 = upd1 + ',' + self._columns[field]._symbol_set[0]
                upd2.append(self._columns[field]._symbol_set[1](vals[field]))
                #for the function fields that receive a value, we set them directly in the database 
                #(they may be required), but we also need to trigger the _fct_inv()
                if (hasattr(self._columns[field], '_fnct_inv')) and not isinstance(self._columns[field], fields.related):
                    #TODO: this way to special case the related fields is really creepy but it shouldn't be changed at
                    #one week of the release candidate. It seems the only good way to handle correctly this is to add an
                    #attribute to make a field `really readonly´ and thus totally ignored by the create()... otherwise
                    #if, for example, the related has a default value (for usability) then the fct_inv is called and it
                    #may raise some access rights error. Changing this is a too big change for now, and is thus postponed
                    #after the release but, definitively, the behavior shouldn't be different for related and function
                    #fields.
                    upd_todo.append(field)
            else:
                #TODO: this `if´ statement should be removed because there is no good reason to special case the fields
                #related. See the above TODO comment for further explanations.
                if not isinstance(self._columns[field], fields.related):
                    upd_todo.append(field)
            if field in self._columns \
                    and hasattr(self._columns[field], 'selection') \
                    and vals[field]:
                self._check_selection_field_value(cr, user, field, vals[field], context=context)
        if self._log_access:
            upd0 += ',create_uid,create_date,write_uid,write_date'
            upd1 += ",%s,(now() at time zone 'UTC'),%s,(now() at time zone 'UTC')"
            upd2.extend((user, user))
        cr.execute('insert into "'+self._table+'" (id'+upd0+") values ("+str(id_new)+upd1+')', tuple(upd2))
        upd_todo.sort(lambda x, y: self._columns[x].priority-self._columns[y].priority)
        
        
        return id_new
    
    
    
'''
class stock_move_split(osv.osv):
    """ stock move split enhanced """

    _inherit = 'stock.move.split'

    def default_get(self, cr, uid, fields, context=None):        
        res = super(stock_move_split, self).default_get(cr, uid, fields, context=context)
        if context.get('active_id'):
            lot_id_passed = context.get('active_id')
            picking_type_passed = context.get('picking_type')
            if 'lot_id_passed' in fields:
                res.update({'lot_id_passed': lot_id_passed}) #,'picking_type_passed':picking_type_passed
        return res
    # Column declarations
    _columns = {
        'lot_id_passed': fields.float('Receivable System Item ID', readonly=True, required=False, help='Text area for rapidly scanned serial numbers'),  
    }
    
'''

class stock_rapid_scan(osv.osv):
    """ rapid scan text box """
    _name = 'stock.rapid.scan'
    
    
    def default_get(self, cr, uid, fields, context=None):
        if context.get('lot_id_passed'):
            # get current lot information
            lot_id_serial = context.get('lot_id_passed')
            move = self.pool.get('stock.move').browse(cr, uid, context['lot_id_passed'], context=context)
            # auto activate use_exisitng serial numbers only when not inbound stock
            use_exist = True
            if (context.get('picking_type') == 'in'):
                use_exist = False  
            return {'lot_id':lot_id_serial,
                'prod_name': move.product_id.name,
                'qty': move.product_qty,
                'check_duplicates': True,
                'qty_per_barcode': 1,
                'picking_type': context.get('picking_type'),
                'use_exist': use_exist }


    # Column declarations
    _columns = {
        'lot_id': fields.integer('Receivable System Item ID', readonly=True, required=False, invisible=True, help='Text area for rapidly scanned serial numbers'),
        #'prod_desc': fields.integer('Product', readonly=True, required=False, help='Product Name'),
        'prod_name': fields.text('Product', readonly=True, required=False, help='Product Name'),         
        'qty': fields.float('Quantity', readonly=True, required=False, help='Qty of Lot'),     
        'check_duplicates': fields.boolean('Check for duplicates', help='Check for duplicates in this scan'),  
        'qty_per_barcode': fields.float('Quantity Per Barcode', readonly=False, required=True, help='Qty per each barcode'),                                                                                                  
        'scanned_numbers': fields.text('Scanned Serial Numbers', readonly=False, required=False, help='Text area for rapidly scanned serial numbers'),  
        'picking_type': fields.char('Picking Type:', readonly=True, required=False, help='Text area for rapidly scanned serial numbers picking type'), 
        'use_exist': fields.boolean('Use existing serial numbers', readonly=False, required=False, help="The system automatically checks this box for you depending if the scan is incoming or outgoing.  You can change it if you want.  Check if items have already been scanned in before.  Uncheck if you want to store a fresh batch.  The system automatically attempt to create serial numbers if they are missing and the box is checked."),                                  
                                         
    }
    
    _defaults = {
        'qty_per_barcode': 1,
        'check_duplicates': True,
    }  
    
    def has_duplicates(self, cr, uid, ids, list_of_values, context={}):  
        value_dict = collections.defaultdict(int)  
        for item in list_of_values:  
            value_dict[item] += 1  
        val = ''
        dup_list = [i for i in value_dict if value_dict[i]!=1] 
        for val in dup_list:
            val += ", "+'\r\n' + val
            raise osv.except_osv(('Barcode Scanner Error'), ("Cannot import numbers because you have duplicates in the list ") + val)
        return any(val > 1 for val in value_dict.itervalues())  
    

    def import_serial_split(self, cr, uid, ids, context={}):
        if context.get('lot_id_passed'):
            # Split the serial numbers
            scanned_numbers = context.get('scanned_numbers')
            serial_list = scanned_numbers.splitlines()
            serial_list = filter(None, serial_list)  #cleanup blanks

            # Count the serial numbers
            serial_list_count = len(serial_list)

            qty = context.get('qty')
            if serial_list_count > qty:
                 ## Raise your error message
                 raise osv.except_osv(('Barcode Scanner Error'),("Cannot import numbers because the number of scanned serial numbers ("+str(serial_list_count)+") is larger than the qty allowed ("+str(qty)+").   \n\nTry deleting the extras or clearing and scanning the actual count.")) 
            # Check for duplicates
            check_duplicates = context.get('check_duplicates')
            if check_duplicates and self.has_duplicates(cr, uid, ids, serial_list, context={}):
                raise osv.except_osv(('Barcode Scanner Error'),("Cannot import numbers because you have duplicates in the list"))

            # Insert the Numbers
            lot_id_serial = context.get('lot_id_passed')
            qty_per_barcode = context.get('qty_per_barcode')
            #move = self.pool.get('stock.move').browse(cr, uid, context['lot_id_passed'], context=context) 

            #if (context.get('picking_type') == 'in'):
            self.split(cr, uid, ids, [lot_id_serial], serial_list, qty_per_barcode, context=None)

            # out and other cases
            #else:
                #self.split_inventory(cr, uid, ids, [lot_id_serial], serial_list, qty_per_barcode, context=None)
        return {'type': 'ir.actions.client',
                'tag': 'reload',}


    # Stock split modified from warehouse stock split to work with parsed scanned text area
    def split(self, cr, uid, ids, move_ids, serial_code_list, qty_per_barcode, context=None):
	print 'CALL'
        if context is None:
            context = {}
        serial_code_list = [serial.strip() for serial in serial_code_list if serial or serial != '']
        #assert context.get('active_model') == 'stock.move',\
        #     'Incorrect use of the stock move split wizard'
        inventory_id = context.get('inventory_id', False)
        prodlot_obj = self.pool.get('stock.production.lot')
        inventory_obj = self.pool.get('stock.inventory')
        move_pool = self.pool.get('stock.move')
        new_move = []
        data = self.read(cr, uid, ids, context=context)[0]
        for move in move_pool.read(cr, uid, move_ids, context=context):
            move_qty = move.get('product_qty', 0)
            quantity_rest = move.get('product_qty', 0)
            uos_qty_rest = move.get('product_uos_qty', 0)
            new_move = []
            total_move_qty = 0.0
            for line in serial_code_list:
                quantity = qty_per_barcode
                total_move_qty += quantity
                if total_move_qty > move_qty:
                    raise osv.except_osv(_('Processing Error!'), _('Serial number quantity %d of %s is larger than available quantity (%d)!') \
                            % (total_move_qty, move['product_id'][1] and move['product_id'][1] or '', move_qty))
                if quantity <= 0 or move_qty == 0:
                    continue
                quantity_rest -= quantity
                uos_qty = quantity / move_qty * move.get('product_uos_qty')
                uos_qty_rest = quantity_rest / move_qty * move.get('product_uos_qty')
                default = {
                    'product_qty': quantity,
                    'product_uos_qty': uos_qty,
                    'state': move['state'],
                    'procurements': [],
                }                
                if quantity_rest < 0:
                    quantity_rest = quantity
                    continue
                elif quantity_rest > 0:
#                    current_move = move_pool.copy(cr, uid, move['id'], default_val, context=context)
                    res = dict(default)
                    for f, colinfo in move_pool._all_columns.items():
                        if f in [ 'create_date', 'write_date']:
                            continue
                        field = colinfo.column
                        if f in default:
                            continue
                        elif isinstance(field, fields.function) or isinstance(field, fields.related):
                            continue
                        elif field._type == 'many2one':
                            res[f] = move[f] and move[f][0]
                        elif field._type == 'one2many':
                            other = self.pool.get(field._obj)
                            lines = [other.copy_data(cr, uid, line_id, context=context) for line_id in sorted(move[f])]
                            res[f] = [(0, 0, ln) for ln in lines if ln]
                        elif field._type == 'many2many':
                            res[f] = [(6, 0, move[f])]
                        else:
                            res[f] = move[f]
                            
                    # Bottlenecking function        
                    current_move = move_pool.create_rapid_insert(cr, uid, res, context=context)
     

                    if inventory_id and current_move:
                        inventory_obj.write(cr, uid, inventory_id, {'move_ids': [(4, current_move)]}, context=context)
                    new_move.append(current_move)
                else:
                    current_move = move['id']
                # If using previous serial numbers attempt to look up and apply
                prod_lot_id = False
                if data['use_exist']:
                    cr.execute("SELECT id FROM stock_production_lot WHERE name = '%s'"%(line))
                    prod_lot_ids = cr.fetchone()
                    prod_lot_id = prod_lot_ids and prod_lot_ids[0] or False
                if not prod_lot_id:
                    prod_lot_id = prodlot_obj.create_rapid_insert(cr, uid, {
                        'name': line,
                        'product_id': move['product_id'][0]},
                    context=context)
#                move_pool.write(cr, uid, [current_move], {'prod_lot_id': prod_lot_id, 'state':move['state']})
                cr.execute('UPDATE stock_move SET prod_lot_id = %s, product_uos_qty = %s, state = %s' \
                                'WHERE id = %s', (prod_lot_id, uos_qty_rest, move['state'], current_move))

                if quantity_rest > 0:
                    cr.execute('UPDATE stock_move SET product_qty = %s, product_uos_qty = %s, state = %s' \
                                'WHERE id = %s', (quantity_rest, uos_qty_rest, move['state'], move['id']))
        return new_move

    # Not being used at the moment
    def split_inventory(self, cr, uid, ids, move_ids, serial_code_list, qty_per_barcode, context=None):
        """ To split stock inventory lines according to serial numbers.

        :param line_ids: the ID or list of IDs of inventory lines we want to split
        """
        if context is None:
            context = {}
        #assert context.get('active_model') == 'stock.inventory.line',\
        #     'Incorrect use of the inventory line split wizard.'
        prodlot_obj = self.pool.get('stock.production.lot')
        ir_sequence_obj = self.pool.get('ir.sequence')
        line_obj = self.pool.get('stock.inventory.line')
        new_line = []
        for data in self.browse(cr, uid, ids, context=context):
            for inv_line in line_obj.browse(cr, uid, move_ids, context=context):
                line_qty = inv_line.product_qty
                quantity_rest = inv_line.product_qty
                new_line = []
                #if data.use_exist:
                #    lines = [l for l in serial_code_list if l]
                #else:
                lines = [l for l in serial_code_list if l]
                for line in lines:
                    quantity = qty_per_barcode
                    if quantity <= 0 or line_qty == 0:
                        continue
                    quantity_rest -= quantity
                    if quantity_rest < 0:
                        quantity_rest = quantity
                        break
                    default_val = {
                        'product_qty': quantity,
                    }
                    if quantity_rest > 0:
                        current_line = line_obj.copy(cr, uid, inv_line.id, default_val)
                        new_line.append(current_line)
                    if quantity_rest == 0:
                        current_line = inv_line.id
                        
                    # If using previous serial numbers attempt to look up and apply    
                    prod_lot_id = False
                    if data.use_exist:
                        prod_lot_ids = prodlot_obj.search(cr, uid, [('product_id.name','=',line.strip())], context=context)
                        prod_lot_id = prod_lot_ids[0]
                        #prod_lot_id = line.prod_lot_id.id
                    if not prod_lot_id:
                        prod_lot_id = prodlot_obj.create(cr, uid, {
                            'name': line,
                            'product_id': inv_line.product_id.id},
                        context=context)
                    line_obj.write(cr, uid, [current_line], {'prod_lot_id': prod_lot_id})
                    prodlot = prodlot_obj.browse(cr, uid, prod_lot_id)

                    update_val = {}
                    if quantity_rest > 0:
                        update_val['product_qty'] = quantity_rest
                        line_obj.write(cr, uid, [inv_line.id], update_val)

        return new_line

    def clear_list(self, cr, uid, ids, context={}):        
        return {'value': {'scanned_numbers': ''}, 'nodestroy': True, 'warning':{'title':'Warning','message':'A button action!'}}

