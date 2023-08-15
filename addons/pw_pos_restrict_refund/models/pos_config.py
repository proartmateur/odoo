# -*- coding: utf-8 -*-
from odoo import api, fields, models


class PosConfig(models.Model):
    _inherit = 'pos.config'


    pw_allow_refund = fields.Boolean(string='Restrict Refund')
    pw_refund_employee_ids = fields.Many2one('hr.employee',string="PW Refund Employees")
    comissionist_ids = fields.Many2many('hr.employee', 'category_id', string='Employees comm')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pw_allow_refund = fields.Boolean(related='pos_config_id.pw_allow_refund', readonly=False)
    #pw_refund_password = fields.Char(related='pos_config_id.pw_refund_password', readonly=False)
    pw_refund_employee_ids = fields.Many2one(related='pos_config_id.pw_refund_employee_ids',readonly=False)
    comissionist_ids = fields.Many2many(related='pos_config_id.comissionist_ids', readonly=False)


class PosSession(models.Model):
    _inherit = 'pos.session'

    def _loader_params_hr_employee_cominess(self):
        if len(self.config_id.employee_ids) > 0:
            domain = ['&', ('company_id', '=', self.config_id.company_id.id), '|', ('user_id', '=', self.user_id.id), ('id', 'in', self.config_id.comissionist_ids.ids)]
        else:
            domain = [('company_id', '=', self.config_id.company_id.id)]

        return {'search_params': {'domain': domain, 'fields': ['name', 'id', 'user_id'], 'load': False}}

    def _get_pos_ui_hr_employee_pedidos(self, params):
        employees = self.env['hr.employee'].search_read(**params['search_params'])
        employee_ids = [employee['id'] for employee in employees]
        user_ids = [employee['user_id'] for employee in employees if employee['user_id']]
        manager_ids = self.env['res.users'].browse(user_ids).filtered(lambda user: self.config_id.group_pos_manager_id in user.groups_id).mapped('id')

        employees_barcode_pin = self.env['hr.employee'].browse(employee_ids).get_barcodes_and_pin_hashed()
        bp_per_employee_id = {bp_e['id']: bp_e for bp_e in employees_barcode_pin}
        for employee in employees:
            employee['role'] = 'manager' if employee['user_id'] and employee['user_id'] in manager_ids else 'cashier'
            employee['barcode'] = bp_per_employee_id[employee['id']]['barcode']
            employee['pin'] = bp_per_employee_id[employee['id']]['pin']

        return employees

    def _pos_data_process(self, loaded_data):
        super()._pos_data_process(loaded_data)
        if self.config_id.module_pos_hr:
            loaded_data['comissionists'] = self._get_pos_ui_hr_employee_pedidos(self._loader_params_hr_employee_cominess())