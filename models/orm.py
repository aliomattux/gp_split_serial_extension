# -*- coding: utf-8 -*-
##############################################################################
# Module by Kranbery Techonolgies LLC
##############################################################################

from osv import osv, fields
import logging

_logger = logging.getLogger(__name__)

class StockModel(osv.Model):
    """Serial Number Related to Stock Move"""

    _inherit='stock.move'

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

        if self._log_access:
            for f in osv.orm.LOG_ACCESS_COLUMNS:
                if vals.pop(f, None) is not None:
                    _logger.warning(
                        'Field `%s` is not allowed when creating the model `%s`.',
                        f, self._name)
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




