# -*- coding: utf-8 -*-
##############################################################################
# Module by Kranbery Techonolgies LLC
##############################################################################

from openerp.osv import osv, fields
#import string
import collections

#from datetime import datetime
import time
import re


class product_pack_search_wizard(osv.osv):
    _name = "product.pack.search.wizard"
    _description = "Product Pack Search and Add Wizard"
    
    _columns = {
        'pack_id': fields.many2one('stock.item.pack', 'Related Pack ID', required=False),    
        #'pack_name': fields.char('Pack ID', size=256, required=False, readonly=True),        
        'item_serial_number': fields.many2one('item.serial', 'Related Serial Number', required=False),  
        'scanned_numbers': fields.text('Scanned Serial Numbers', readonly=False, required=False, help='Text area for rapidly scanned serial numbers'),  
        'instructions': fields.text('', readonly=True, required=False, help='Text area for rapidly scanned serial numbers'),  
    }
        
    _defaults = {
        'instructions':'You can search by either using existing pack number or a serial that is part of a pack.  You may see duplicate serial numbers, but you can test each and see the result in the window'         
    }
                            
        
    def search_and_load_pack(self, cr, uid, ids, context={}):

        #stock_item_serial = self.pool.get('stock.item.serial')
        #stock_item_serial_ids = stock_item_serial.search(cr, uid, [('move_id','=',move_id)])
        stock_item_serial = self.pool.get('stock.item.serial')
        serial_list = ''
        for msnw in self.browse(cr, uid, ids): 
            
            # Search and get related serials
            try:
                if msnw.item_serial_number:                
                    stock_item_serial_ids = stock_item_serial.search(cr, uid, [('name','=',msnw.item_serial_number.id)])
                    if stock_item_serial_ids:
                        serial_numbers_obj = stock_item_serial.browse(cr, uid, stock_item_serial_ids)
                        pack_id = serial_numbers_obj[0].pack_id
                        stock_item_serial_ids = stock_item_serial.search(cr, uid, [('pack_id','=',pack_id.strip())])
                        
                                 
                # Search and get pack serials
                elif msnw.pack_id:                
                    stock_item_serial_ids = stock_item_serial.search(cr, uid, [('pack_id','=',msnw.pack_id.name.strip())])

                
                if stock_item_serial_ids:
                    serial_numbers_obj = stock_item_serial.browse(cr, uid, stock_item_serial_ids)                
                    for serial in serial_numbers_obj:
                
                        # output pack number if it exists
                        if serial.pack_id:
                            pack_number = serial.pack_id
                        else:
                            pack_number = ''                    

                        if serial.name:                  
                            serial_number = serial.name.name
                        else:
                            serial_number = ''
                    
                        # merge the two for writing    
                        serial_list += serial_number.strip() +'\t\t'+ pack_number.strip()+'\n'
                else:
                    raise osv.except_osv(('Pack Search'), ("No related pack of serial numbers were found"))
            except Exception:
                    raise osv.except_osv(('Pack Search'), ("No related pack of serial numbers were found"))

        self.write(cr, uid, ids, {'pack_id':'', 'item_serial_number':'','scanned_numbers':serial_list}, context)

        return {
        'name':("Lot Search"),
        'view_mode': 'form',
        'view_id': False,
        'res_id': ids[0],
        'view_type': 'form',
        'res_model': 'product.pack.search.wizard',
        'type': 'ir.actions.act_window',
        'target': 'new',
        'domain': '[]',
        'context': context,                 
            }    

    def load_pack(self, cr, uid, ids, pack_name, context={}):    
        # popluate associated serial numbers on load of popup form
        serial_list = ''
        pack_number = ''
        serial_number = ''
        move_id = context.get('active_id', False)
        stock_item_serial = self.pool.get('stock.item.serial')
        stock_item_serial_ids = stock_item_serial.search(cr, uid, [('move_id','=',move_id)])
        if stock_item_serial_ids != []:
            serial_numbers_obj = stock_item_serial.browse(cr, uid, stock_item_serial_ids)                
            for serial in serial_numbers_obj:
                
                # output pack number if it exists
                if serial.pack_id:
                    pack_number = serial.pack_id
                else:
                    pack_number = ''                    

                if serial.name:                   
                    serial_number = serial.name.name
                else:
                    serial_number = ''
                    
                # merge the two for writing    
                serial_list += serial_number +'\t\t'+ pack_number+'\n'
        return serial_list
            
    def search_and_add_pack(self, cr, uid, ids, context={}):
        
        serial_number_pack_list = ''
        base_serial_list = context.get('base_serial_list')
        parent_ids = context.get('parent_ids')
        pack_number = ''

        # In the case of empty numbers
        if not base_serial_list:
                base_serial_list = ''        
        
        # build pack serial list        
        for msnw in self.browse(cr, uid, ids):            
            if msnw.scanned_numbers:
                serial_list = msnw.scanned_numbers.splitlines()
                serial_list = filter(None, serial_list)  #cleanup blanks
                for serial_number in serial_list:
                                   
                    # make new list    
                    serial_number_pack_list += serial_number +'\t\t'+ pack_number+'\n'
        
        # Write back to parent wizard
        product_serial_number_wizard = self.pool.get('product.serial.number.wizard')              
        product_serial_number_wizard.write(cr, 1, parent_ids, {'scanned_numbers':serial_number_pack_list+base_serial_list}, context)    
            
            
        return {
        'name':("Serial Numbers"),
        'view_mode': 'form',
        'res_id': parent_ids[0],
        'view_type': 'form',
        'res_model': 'product.serial.number.wizard',
        'type': 'ir.actions.act_window',
        'target': 'new',
        'domain': '[]',
        'context': context,                 
            }
                
    def cancel_pack_search_wizard(self, cr, uid, ids, context={}):
        
        # Turn off bypass_validation for effective save
        context['bypass_validation'] = False
        
        # Lock Sequence            
        context['lock_sequence_increment'] = True
        
        # Passed context Var
        base_serial_list = context.get('base_serial_list')
        parent_ids = context.get('parent_ids')
            
        # return the list back
        product_serial_number_wizard = self.pool.get('product.serial.number.wizard')              
        product_serial_number_wizard.write(cr, 1, parent_ids, {'scanned_numbers':base_serial_list}, context)    
            
            
        return {
        'name':("Serial Numbers"),
        'view_mode': 'form',
        'view_id': False,
        'res_id': parent_ids[0],
        'view_type': 'form',
        'res_model': 'product.serial.number.wizard',
        'type': 'ir.actions.act_window',
        'target': 'new',
        'domain': '[]',
        'context': context,                 
            }


class product_serial_number_wizard(osv.osv_memory):
    _name = "product.serial.number.wizard"
    _description = "Product Serial Number Wizard"
    #_inherit = "stock.move"

    def name_get(self, cr, uid, ids, context=None):
        res = []
        for msnw in self.browse(cr, uid, ids, context=context):
            res.append((msnw.id, msnw.move_id.name))
        return res

    def _product_default_get(self, cr, uid, ids, context=None):
        move_obj = self.pool.get('stock.move')
        for move in move_obj.browse(cr, uid, [context['active_id']]):
            res = move.product_id.id
        return res

    def _msn_mfg_get(self, cr, uid, ids, context=None):
        
        # popluate associated serial numbers on load of popup form
        move_id = context.get('active_id', False)
        stock_item_serial = self.pool.get('stock.item.serial')
        stock_item_serial_ids = stock_item_serial.search(cr, uid, [('move_id','=',move_id)])
        if stock_item_serial_ids != []:
            serial_numbers_obj = stock_item_serial.browse(cr, uid, stock_item_serial_ids)   
            for serial in serial_numbers_obj:                        
                return serial.mfg_product_code     
    
    def _msn_ids_get(self, cr, uid, ids, context=None):
        
        # scrapped
        scrap = False
        if context.get('scrap'): 
            scrap = context.get('scrap')
            
        # popluate associated serial numbers on load of popup form
        serial_list = ''
        pack_number = ''
        serial_number = ''
        move_id = context.get('active_id', False)
        stock_item_serial = self.pool.get('stock.item.serial')
        stock_item_serial_ids = stock_item_serial.search(cr, uid, [('move_id','=',move_id), ('scrapped','=',scrap)])
        if stock_item_serial_ids != []:
            serial_numbers_obj = stock_item_serial.browse(cr, uid, stock_item_serial_ids)                
            for serial in serial_numbers_obj:
                
                # output pack number if it exists
                if serial.pack_id:
                    pack_number = serial.pack_id
                else:
                    pack_number = ''                    

                if serial.name:                   
                    serial_number = serial.name.name
                else:
                    serial_number = ''
                    
                # merge the two for writing    
                serial_list += serial_number +'\t\t'+ pack_number+'\n'
                
                
        #context['base_serial_list'] = serial_list           
        # preloaded from other calls

        #serial_list = context.get('base_serial_list');                    
        return serial_list    

        
    def _use_exist_set(self, cr, uid, ids, context=None):
        # if (context.get('picking_type') == 'in'):
        #     use_exist = True
        # else:
        #     use_exist = False  
        # return use_exist
        # Set serial to use previously used SN's if scanning out but make available just in case
        #scanned_numbers_exist_in_list = False
        #if context.get('active_id'):            
        #    for msnw in self.browse(cr, uid, ids):
        #        if msnw.scanned_numbers:
        #            scanned_numbers_exist_in_list = True
        #        else:
        #            scanned_numbers_exist_in_list = False
        
        return True #(not (context.get('picking_type') == 'in')) or scanned_numbers_exist_in_list

    def _get_move_line_qty(self, cr, uid, ids, context=None): 
        active_id = context.get('active_id')  
        if active_id: 
            if context.get('scrapped_product_qty'):       
                return context.get('scrapped_product_qty')
            else:
                return self.pool.get('stock.move').browse(cr, uid, active_id, context=context).product_qty
        
    def _check_if_existing(self, cr, uid, ids, context=None):         
        active_id = context.get('active_id')  
        if active_id: 
            # Check if serials exist for this move line
            stock_item_serial = self.pool.get('stock.item.serial')
            stock_item_serial_ids = stock_item_serial.search(cr, uid, [('move_id','=',active_id)])
            if stock_item_serial_ids:
                return True
            else:
                return False

    #def update_qty(self, cr, uid, ids, context=None):
    #    return {'use_exist':True}

    _columns = {
        'move_id': fields.many2one('stock.move','Referential Move ID'),
        'product_id': fields.many2one('product.product', 'Product',),
        'line_ids': fields.one2many('serial.number.wizard', 'msnw_id', 'Serial Numbers'),
        'creation_date': fields.date('Creation Date'),
	'picking_type_id': fields.many2one('stock.picking.type', 'Picking Type'),
        
        # rapid barcode scanner
        'qty': fields.float('Quantity Expected', readonly=True, required=False, help='Qty of Lot'), 
        'force_qty': fields.boolean('Force Serial Number Count', help='The system checks to make sure the number of serial numbers is equal to the quantity.  You can bypass a different qty count but its not advised because pieces of quantity in the shipment will not be tracked'),
        'use_exist': fields.boolean('Use Existing', help='The system automatically checks or unchecks this box for you depending if the scan is incoming (Getting Product), internal (Internal Move) or outgoing (Delivering Product).  You can change it if you want.  Check if items have already been scanned in before.  Uncheck if you want to create a new batch of Serial Numbers.  The system automatically attempt to create serial numbers if they are missing and the box is checked.'),             
        'check_duplicates': fields.boolean('Check for Duplicates', help='Check for duplicates in this scan'),
        
        'mfg_product_code': fields.char('Manufacture Product Code', size=128, required=False),          
        'scanned_numbers': fields.text('Scanned Serial Numbers', readonly=False, required=False, help='Text area for rapidly scanned serial numbers'),  
        'initial_created': fields.boolean('Initial List Created'),
        
        # Packing
        'pack_id': fields.many2one('stock.item.pack', 'Stock Pack'),
     
    }

    _defaults = {
        'move_id': lambda x, y, z, c: c.get('active_id', False),
        'product_id': lambda self, cr, uid, c: self._product_default_get(cr, uid, [c.get('active_id', False)], context=c),
        'picking_type_id': lambda x, y, z, c: c.get('picking_type_id', False),
        'qty': lambda self, cr, uid, c: self._get_move_line_qty(cr, uid, [], context=c),
        'use_exist': lambda self, cr, uid, c: self._use_exist_set(cr, uid, [], context=c),
        'check_duplicates': True,
        'force_qty': False,
        'initial_created': lambda self, cr, uid, c: self._check_if_existing(cr, uid, [], context=c),
        'creation_date': lambda *a: time.strftime('%Y-%m-%d %H:%M:%S'),
        'scanned_numbers': lambda x, y, z, c: x._msn_ids_get(y, z, [], context=c),
        'mfg_product_code': lambda x, y, z, c: x._msn_mfg_get(y, z, [], context=c),                
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
    

    def save_serial_number_wizard(self, cr, uid, ids, context={}):
        if context.get('active_id'):
            bypass_validation = context.get('bypass_validation')
            
            
             
            
            for msnw in self.browse(cr, uid, ids):
                
                # Split the serial numbers        
                if not msnw.scanned_numbers and not bypass_validation:
                    raise osv.except_osv(('Serial Number Error'),("There are no numbers scanned into the system"))
                 
                # make sure there is something in here 
                if not msnw.scanned_numbers:
                    return{}
                    
                if not msnw.scanned_numbers.strip():
                    return{}
                                   
                
                serial_list = msnw.scanned_numbers.splitlines()
                serial_list = filter(None, serial_list)  #cleanup blanks
                
                # Count the serial numbers
                serial_list_count = len(serial_list)
                qty = msnw.qty
                if not msnw.force_qty and not bypass_validation:
                    if serial_list_count != qty:
                        raise osv.except_osv(('Serial Number Error'),("Cannot import numbers because the number of scanned serial numbers ("+str(serial_list_count)+") does not equal the expected stock amount ("+str(qty)+").   \n\nTry deleting the extras or clearing and scanning the actual count.")) 
            
                # Check for duplicates
                if not bypass_validation:
                    check_duplicates = msnw.check_duplicates
                    if check_duplicates and self.has_duplicates(cr, uid, ids, serial_list, context={}):
                        raise osv.except_osv(('Serial Number Error'),("Cannot import numbers because you have duplicates in the list"))

                # Insert the Numbers
                #move = self.pool.get('stock.move').browse(cr, uid, context['lot_id_passed'], context=context) 

                #if (context.get('picking_type') == 'in'):
                move_id = context.get('active_id')            
                
                # Save Serial number
                self.serial_create(cr, uid, ids, [move_id], serial_list, msnw.mfg_product_code, msnw.use_exist, context)
                
                # out and other cases
                #else:
                    #self.split_inventory(cr, uid, ids, [lot_id_serial], serial_list, qty_per_barcode, context=None)

   
            return {}    
    
        
                

    # Stock split modified from warehouse stock split to work with parsed scanned text area
    def serial_create(self, cr, uid, ids, move_ids, serial_code_list, mfg_product_code, use_exist, context=None):
        if context is None:
            context = {}  
            
        res = ''   
        
        # Process Serial Numbers
        if serial_code_list:
            item_serial = self.pool.get('item.serial')            
            stock_item_serial = self.pool.get('stock.item.serial')
            #stock_item_pack = self.pool.get('stock.item.pack')
            
            product_id = context.get('product_id')

            
            # Add or use existing Serial Number
            for line in serial_code_list: 
                
                serial_number = line.split('\t\t')[0].strip()
                if (len(line.split('\t\t')) > 1):
                    pack_number = line.split('\t\t')[1].strip()
                else:
                    pack_number = ''

                # Ensure pack exists, if not then attempt to create new pack
                #if pack_number:
                #    product_id = context.get("product_id")
                #    item_pack_ids = stock_item_pack.search(cr, uid, [('name','=',pack_number)], context=context)
                #    if item_pack_ids:
                #        pack_id = item_pack_ids[0]
                #    else: 
                #        pack_id = stock_item_pack.create(cr, uid, {'name': 654546, 'product_id': product_id,'qty':-1},context=context)

                item_serial_ids = item_serial.search(cr, uid, [('name','=',line.strip()),('product_id','=',product_id)], context=context)
                if use_exist:                
                    if not item_serial_ids:
                        # Add to overall serial number record 
                        res = item_serial.create(cr, uid, {'name': serial_number, 'product_id':product_id,'created_move_id': move_ids[0]},context=context)                         
                else:
                    
                    # Add to overall serial number record 
                    res = item_serial.create(cr, uid, {'name': serial_number, 'product_id':product_id,'created_move_id': move_ids[0]},context=context)                                 
                
                if res:
                    serial_ref = res
                else:
                    serial_ref = item_serial_ids[0]
                  
                # Mark as scrapped    
                scrapped = False
                if context.get('scrap'):       
                    scrapped = context.get('scrap')
                
                
                # Add to serial list for move item           
                stock_item_serial.create(cr, uid, {'name': serial_ref, 'mfg_product_code':mfg_product_code,'pack_id':pack_number,'move_id': move_ids[0], 'scrapped': scrapped},context=context)
                #stock_item_serial.write(cr, uid, {'name': serial_ref, 'mfg_product_code':mfg_product_code,'pack_id':pack_number,'move_id': move_ids[0]}, context=context)                                
                # Move serial number tracking create - testing
                #self.serial_create_move_history(cr, uid, ids, move_ids, line, use_exist, context=None)
                #serial_move.create(cr, uid, {'name': line, 'committed': True, 'move_id': [move_ids]},context=context)
                
               
                
                
        # Empty scan list                    
        else:
            raise osv.except_osv(('Serial Number Error'),("The List is Empty. Please insert serial numbers or cancel."))
        return True      

    # Stock split modified from warehouse stock split to work with parsed scanned text area
    def serial_create_move_history(self, cr, uid, ids, move_ids, serial_number, use_exist, context=None):
	print 'CALL'
        if context is None:
            context = {}  
        
        stock_move = self.pool.get('stock.move')
        
        
        # Process Serial Numbers
        if serial_number:
            
            move_obj = stock_move.browse(cr, uid, move_ids[0])   

            self.pool.get('serial.move').create_rapid_insert(cr, uid, {
'serial_number':serial_number,
'move_id':move_ids[0],
'name':move_obj.name,
'priority':move_obj.priority,
'create_date':move_obj.create_date,
'date':move_obj.date,
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
#'auto_validate':move_obj.auto_validate,
'move_dest_id':move_obj.move_dest_id.id,
'picking_id':move_obj.picking_id.id,
'note':move_obj.note,
'state':move_obj.state,
'price_unit':move_obj.price_unit,
#'price_currency_id':move_obj.price_currency_id.id,
'company_id':move_obj.company_id.id,
'backorder_id':move_obj.backorder_id.id,
'origin':move_obj.origin,
'scrapped': move_obj.scrapped,
'picking_type_id':move_obj.picking_type_id.id,


},
        context=context)    
                                                
        return True        

    def cancel_serial_number_wizard(self, cr, uid, ids, context={}):
        return {}   


    def redo_serial_number_wizard(self, cr, uid, ids, context={}):
         
        # Check as scrapped    
        scrapped = False
        if context.get('scrap'):       
            scrapped = context.get('scrap') 
         
         
        move_id = context.get('active_id', False)
        if move_id: 
            # Remove Item Serial from Registry if created
            #item_serial = self.pool.get('item.serial')
            #item_serial_ids = item_serial.search(cr, uid, [('created_move_id','=',move_id)])
            #item_serial.unlink(cr, uid, item_serial_ids, context=None)
        
            # Remove Item Serials from move relation list 
            stock_item_serial = self.pool.get('stock.item.serial')
            stock_item_serial_ids = stock_item_serial.search(cr, uid, [('move_id','=',move_id),('scrapped','=',scrapped)])
            stock_item_serial.unlink(cr, uid, stock_item_serial_ids, context=None)
            
            # Remove Item Serials from Tracking List
            stock_item_serial_move = self.pool.get('serial.move')
            stock_item_serial_move_ids = stock_item_serial_move.search(cr, uid, [('move_id','=',move_id)])
            stock_item_serial_move.unlink(cr, 1, stock_item_serial_move_ids, context=None)

            # Save new set of serial numbers
            self.save_serial_number_wizard(cr, uid, ids, context)        
        
        
        #self.unlink(cr, uid, ids, context=None)
        #self.write(cr, uid, ids, {'scanned_numbers': ''}, context=context)         
                       

        # return to scrapped form if scrapped
        if scrapped:
            parent_init_ids = context.get('parent_init_ids')
            return {
                    'name':("Scrap Move"),
                    'view_mode': 'form',
                    'view_id': False,
                    'res_id': parent_init_ids[0],                       
                    'view_type': 'form',
                    'res_model': 'stock.move.scrap',                 
                    'type': 'ir.actions.act_window',
                    'target': 'new',
                    'domain': '[]',
                    'context': context,                                                    
            }   
       
        else:            
            return {}                        
  

    def add_a_pack(self, cr, uid, ids, context={}):
        
        # turn off validation to temporarily save current serial list
        context['bypass_validation'] = True
        context['lock_sequence_increment'] = False
        
        
        for msnw in self.browse(cr, uid, ids): 
            context['mfg_product_code'] = msnw.mfg_product_code
            context['base_serial_list'] = msnw.scanned_numbers
            context['parent_ids'] = ids
            
            
            
        #self.redo_serial_number_wizard(cr, uid, ids, context)
        
        
                  

                       
        return {
        'name':("Add to Pack"),
        'view_mode': 'form',
        'view_id': False,
        'view_type': 'form',
        'res_model': 'product.pack.number.wizard',
        'type': 'ir.actions.act_window',
        'nodestroy': False,
        'target': 'new',
        'domain': '[]',
        'context': context,                
                                        
        } 
    
    def search_pack(self, cr, uid, ids, context={}):
        
        # turn off validation to temporarily save current serial list
        context['bypass_validation'] = True
        context['lock_sequence_increment'] = False
        
        
        for msnw in self.browse(cr, uid, ids): 
            context['mfg_product_code'] = msnw.mfg_product_code
            context['base_serial_list'] = msnw.scanned_numbers
            context['parent_ids'] = ids
                                
                
        return {
        'name':("Pack Search"),
        'view_mode': 'form',
        'view_id': False,
        'view_type': 'form',
        'res_model': 'product.pack.search.wizard',
        'type': 'ir.actions.act_window',
        'nodestroy': False,
        'target': 'new',
        'domain': '[]',
        'context': context,                 
            }    



class product_pack_number_wizard(osv.osv):
    _name = "product.pack.number.wizard"
    _description = "Product Pack Number Wizard"

    def _use_exist_set(self, cr, uid, ids, context=None):
        # if (context.get('picking_type') == 'in'):
        #     use_exist = True
        # else:
        #     use_exist = False  
        # return use_exist
        # Set serial to use previously used SN's if scanning out but make available just in case
        scanned_numbers_exist_in_list = False
        if context.get('active_id'):            
            for msnw in self.browse(cr, uid, ids):
                if msnw.scanned_numbers:
                    scanned_numbers_exist_in_list = True
                else:
                    scanned_numbers_exist_in_list = False
        
        return (not (context.get('picking_type') == 'in')) or scanned_numbers_exist_in_list


    def _get_next_pack_id(self, cr, uid, ids, context):
        
        # Need sequence increment locks to keep wizard actions from setting the wrong number
        lock_sequence_increment = context.get('lock_sequence_increment')        
        if not lock_sequence_increment:
            new_id = self.pool.get('ir.sequence').get(cr, uid, 'product.pack.number.wizard')        
	#for some reason context is a frozen dict which isnt a native supported type
	#but some functionality odoo provides. We need to change the context of course so convert
	#back to a dict
	s = dict(context)
	del context
	context = s
	#Solves migration issue
        context['lock_sequence_increment'] = True
        return new_id

    def _get_next_pack_qty(self, cr, uid, ids, context):
        if context.get('pack_qty'):
            return context.get('pack_qty')
        else:
            return 0.0    
        

    _columns = {

        'pack_name': fields.char('Pack ID', size=256, required=True, readonly=True),            
        'scanned_numbers': fields.text('Scanned Serial Numbers', readonly=False, required=False, help='Text area for rapidly scanned serial numbers'),  
        'check_duplicates': fields.boolean('Check for Duplicates', help='Check for duplicates in this scan'),
        'use_exist': fields.boolean('Use Existing', help='The system automatically checks or un-checks this box for you depending if the scan is incoming (Getting Product), internal (Internal Move) or outgoing (Delivering Product).  You can change it if you want.  Check if items have already been scanned in before.  Uncheck if you want to create a new batch of Serial Numbers.  The system automatically attempt to create serial numbers if they are missing and the box is checked.'),             

        
        
        # Range Count
        'scanned_range_start': fields.char('Range Serial Start', size=128, required=False),
        'scanned_range_end': fields.char('Range Serial End', size=128, required=False), 
        'qty': fields.float('Pack QTY', readonly=False, required=False, help='Qty of Lot'), 
    }

    _defaults = {
        'check_duplicates': True,
        'use_exist': lambda self, cr, uid, c: self._use_exist_set(cr, uid, [], context=c),
        'pack_name': lambda self, cr, uid, c: self._get_next_pack_id(cr, uid, [], context=c),
        'qty': lambda self, cr, uid, c: self._get_next_pack_qty(cr, uid, [], context=c),
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
    
    
    def save_pack_number_wizard(self, cr, uid, ids, context={}):
        serial_number_pack_list = ''
        base_serial_list = context.get('base_serial_list')
        parent_ids = context.get('parent_ids')
        pack_number = self.pack_create(cr, uid, ids, context)    

        # In the case of empty numbers
        if not base_serial_list:
                base_serial_list = ''
        
        
        # build pack serial list        
        for msnw in self.browse(cr, uid, ids):            
            if msnw.scanned_numbers:
                serial_list = msnw.scanned_numbers.splitlines()
                serial_list = filter(None, serial_list)  #cleanup blanks
                
                # Ensure qty matches
                serial_list_count = len(serial_list)
                if serial_list_count != msnw.qty:
                    raise osv.except_osv(('Serial Number Error'),("Cannot import numbers because the number of scanned serial numbers ("+str(serial_list_count)+") does not equal the expected qty in the box ("+str(msnw.qty)+").   \n\nTry deleting the extras or clearing and scanning the actual count."))

                if msnw.check_duplicates and self.has_duplicates(cr, uid, ids, serial_list, context={}):
                    raise osv.except_osv(('Serial Number Error'),("Cannot import numbers because you have duplicates in the list"))
                # make new list                  
                for serial_number in serial_list:                                                        
                    serial_number_pack_list += serial_number +'\t\t'+ pack_number+'\n'
        
        # Write back to parent wizard
        product_serial_number_wizard = self.pool.get('product.serial.number.wizard')              
        product_serial_number_wizard.write(cr, 1, parent_ids, {'scanned_numbers':serial_number_pack_list+base_serial_list}, context)    
            
            
        # Store pack qty so that it's easy to recall automatically
        context['pack_qty'] = msnw.qty
            
        return {
        'name':("Serial Numbers"),
        'view_mode': 'form',
        'view_id': False,
        'res_id': parent_ids[0],
        'view_type': 'form',
        'res_model': 'product.serial.number.wizard',
        'type': 'ir.actions.act_window',
        'target': 'new',
        'domain': '[]',
        'context': context,                 
            }
       

    def pack_create(self, cr, uid, ids, context=None):
        
        if context.get('active_id'):        
            product_id = context.get('product_id')
            mfg_product_code = context.get('mfg_product_code')
            stock_item_pack = self.pool.get('stock.item.pack') 

            msnw = self.browse(cr, uid, ids)[0]
            pack_name = msnw.pack_name.strip()
            stock_item_pack.create(cr, uid, {'name': pack_name, 'mfg_product_code':mfg_product_code,'product_id': product_id,'qty':msnw.qty},context=context)
        return pack_name 
        

    def cancel_pack_number_wizard(self, cr, uid, ids, context={}):
        
        # Turn off bypass_validation for effective save
        context['bypass_validation'] = False
        
        # Lock Sequence            
        context['lock_sequence_increment'] = True
        
        # Passed context Var
        base_serial_list = context.get('base_serial_list')
        parent_ids = context.get('parent_ids')
            
        # return the list back
        product_serial_number_wizard = self.pool.get('product.serial.number.wizard')              
        product_serial_number_wizard.write(cr, 1, parent_ids, {'scanned_numbers':base_serial_list}, context)    
            
            
        return {
        'name':("Serial Numbers"),
        'view_mode': 'form',
        'view_id': False,
        'res_id': parent_ids[0],
        'view_type': 'form',
        'res_model': 'product.serial.number.wizard',
        'type': 'ir.actions.act_window',
        'target': 'new',
        'domain': '[]',
        'context': context,                 
            }



    def increment_string(self, cr, uid, ids, s, context={}):
        lastNum = re.compile(r'(?:[^\d]*(\d+)[^\d]*)+')
        
        """ look for the last sequence of number(s) in a string and increment """
        m = lastNum.search(s)
        if m:
            next_num = str(int(m.group(1))+1)
            start, end = m.span(1)
            s = s[:max(end-len(next_num), start)] + next_num + s[end:]
        return s        

    def auto_fill_serial_range(self, cr, uid, ids, context={}):

            
        for msnw in self.browse(cr, uid, ids):
            if not msnw.scanned_range_start:                        
                raise osv.except_osv(('Auto Range Error'),("You need to have at least a serial number in 'Range Serial Start'.  \n\n You can use either 'Range Serial End' or 'Pack Qty' to generate the size of numbers in the range.")) 
            
            serial_numbers = ''
            
            # use end box
            if msnw.scanned_range_end:
                inc = (msnw.scanned_range_start);
                serial_numbers = inc+'\n'
                
                end_count = (msnw.scanned_range_end)
                count = 0
                            
                while (inc != end_count) and (count <= 30000):
                    inc = self.increment_string(cr, uid, ids, inc, context={})
                    serial_numbers = serial_numbers + inc+'\n'
                    count = count + 1                    
                    if count >= 30000:
                        raise osv.except_osv(('Auto Range Error'),("System is stopping at 30,000. Either you have a lot of stock or the ending range is not working")) 
                count = count+1
                   
            # use qty box
            elif msnw.qty:
                inc = (msnw.scanned_range_start);
                serial_numbers = inc+'\n'
                end_count = msnw.qty
                count = 1
                while count < end_count:
                    inc = self.increment_string(cr, uid, ids, inc, context={})
                    serial_numbers = serial_numbers + inc+'\n'
                    count = count+1   
                    
            else:
                raise osv.except_osv(('Auto Range Error'),("Please enter either an ending serial number or qty"))     
                        
        
        # Turn off bypass_validation for effective save
        context['bypass_validation'] = False
         
        # Lock Sequence            
        context['lock_sequence_increment'] = True        
        self.write(cr, uid, ids, {'scanned_range_start':'', 'scanned_range_end':'', 'qty':count,'scanned_numbers':serial_numbers}, context)
        
        # Store pack qty so that it's easy to recall automatically
        context['pack_qty'] = msnw.qty

        return {
        'name':("Add to Pack"),
        'view_mode': 'form',
        'view_id': False,
        'res_id': ids[0],
        'view_type': 'form',
        'res_model': 'product.pack.number.wizard',
        'type': 'ir.actions.act_window',
        'target': 'new',
        'domain': '[]',
        'context': context,                 
            }    


class serial_number_wizard(osv.osv_memory):
    _name = "serial.number.wizard"
    _description = "Serial number"

    _columns = {
        'name': fields.char('Serial Number', size=64),
        'msnw_id': fields.many2one('product.serial.number.wizard', 'msnW'),
    }

