# -*- coding: utf-8 -*-

from odoo import models, fields, api


class contacts_sync(models.Model):
    _name = 'contacts.sync'
    _description = 'contacts.sync'

    name = fields.Char()
    api_url = fields.Char()
    api_username = fields.Char()
    api_password = fields.Char()
    sync_type = fields.Char()
    description = fields.Text()
    is_current_active = fields.Boolean()

    # region Form Methods
    def sync_all_contacts(self):
        if self.sync_type != 'massive':
            return self.notify_danger('Ups!', 'Solamente se pueden sincronizar todos los contactos cuando el tipo de actualización es atómico. Presione click sobre el botón: "HABILITAR MASIVO" y vuelva a intentarlo nuevamente.')
        print("------> Sincronizando..........")
        return self.notify_success("Listo","¡Todos los contactos fueron sincronizados!")

    #region Notifications
    def show_notification(self, title:str, message:str, type:str):
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': title,
                'message': message,
                'type': type, #types: success,warning,danger,info
                'sticky': False,
            }
        }

    def notify_danger(self, title, message):
        return self.show_notification(title, message, 'danger')

    def notify_success(self, title, message):
        return self.show_notification(title, message, 'success')

    def notify_warning(self, title, message):
        return self.show_notification(title, message, 'warning')

    #endregion
    def set_massive_available(self):
        self.sync_type = 'massive'
        self.description = f"""Sincronización Masiva
        Este tipo de sincronización bloquea los eventos: (Cuando se crea un contacto) y (Cuando se actualiza un contacto)
        con la finalidad de prevenir un ciclo infinito de actualizaciones entre Odoo y {self.name}.
        
        Al presionar click en el botón "SINCRONIZAR TODOS" se comenzará a sicronizar todos los contactos de Odoo con {self.api_url}
        dando como resultado final la misma información en ambos sistemas.
        Se dará prioridad a la información de Odoo, por lo que si algún contacto existe previamente en {self.name}
        su información será sobreescrita con la versión de Odoo.
        En caso de que el contacto solamente exista en {self.name} este se creará en Odoo con la misma información.
        """

    def set_atomic_available(self):
        self.sync_type = 'atomic'
        self.description = f"""Sincronización Atómica
                Este tipo de sincronización detecta los eventos en Odoo: (Cuando se crea un contacto) y (Cuando se actualiza un contacto)
                Al momento de ejecturase, va a sobreescribir la información del contacto existente en {self.name}.
                En caso de no existir en {self.name} se creará un nuevo contacto con la información de Odoo.
                """

    def set_active_current(self):
        self.is_current_active = True
        id = self.id
        for record in self.search([]):
            print("record.id:")
            print(record.id)
            if record.id != id:
                record.is_current_active = False
    # endregion
