# -*- coding: utf-8 -*-

from odoo import models, fields, api
import requests
from dataclasses import dataclass


class AgendaProRepository:
    def __int__(self):
        pass

    def search(self, email: str, mode='exist'):
        if mode == 'exist':
            return AgendaProDto(
                id=333,
                first_name="",
                last_name="",
                email=email,
                identification_number="NIF",
                phone="",
                second_phone="",
                age=33,
                birth_day=None,
                birth_month=None,
                birth_year=None,
                record_number="añsdfkañdskfjañdskfjañksdj",
                address="",
                district="The District",
                city="",
                custom_attributes=[],
            )
        return None

@dataclass
class AgendaProDto:
    id: int
    first_name: str
    last_name: str
    email: str
    identification_number: str
    phone: str
    second_phone: str
    age: int
    birth_day: None
    birth_month: None
    birth_year: None
    record_number: str
    address: str
    district: str
    city: str
    custom_attributes: list[str]

    def mergeForUpdateAgenda(self, existent):
        self.id = existent.id
        self.identification_number = existent.identification_number
        self.age = existent.age
        self.birth_day = existent.birth_day
        self.birth_month = existent.birth_month
        self.birth_year = existent.birth_year
        self.record_number = existent.record_number
        self.district = existent.district
        self.custom_attributes = existent.custom_attributes

def mapPartnerToAgendaPro(record) -> AgendaProDto:
    name_parts = record.name.split(' ')
    first_name = name_parts[0]
    last_name = ' '.join(name_parts[1:])
    address = f"{record.street} {record.street2} {record.zip}"
    return AgendaProDto(
        id=0,
        first_name=first_name,
        last_name=last_name,
        email=record.email,
        identification_number='From Agenda',
        phone=record.phone,
        second_phone=record.mobile,
        age=0,
        birth_day=None,
        birth_month=None,
        birth_year=None,
        record_number='From Agenda',
        address=address,
        district='From Agenda',
        city=record.city,
        custom_attributes=[],
    )

class Aprueba(models.Model):
    _name = 'a_prueba.a_prueba'
    _description = 'desc a_prueba.a_prueba'

    name = fields.Char()
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()

    @api.depends('value')
    def _value_pc(self):
        for record in self:
            record.value2 = float(record.value) / 100

    @api.depends('value')
    def _compute_total(self):
        print("----- SOME ACTION")
        print("----- SOME ACTION ----------------")
        return 1000

    def set_massive_available(self):
        self.description = "Sync Massive"

    def set_atomic_available(self):
        self.description = "Sync Atomic"

    def sync_contacts(self):
        print(self.description)
        if(self.description != "Sync Massive"):
            print("No se puede sincronizar masivamente")
            return 1
        contacts = self.env['res.partner'].search([])
        print("askdfasdhfladflahdfljahdlsj")
        print(contacts)
        for contact in contacts:
            print(contact.name)
            print(contact.id)
            if contact.id == 45:
                contact.name += "889"
                break
        print("--------------")

        print("--------------")
        #self.description = ''


    @staticmethod
    def do_some(record, sync_actions):
        print("Sync Atomic:")
        print(sync_actions)
        if(sync_actions.description == 'Sync Massive'):
            print("Ya se está sincronizando masivamente")
            return 1
        repo = AgendaProRepository()
        existent = repo.search(record.email, mode='exist')
        dto = mapPartnerToAgendaPro(record)

        if existent is None:
            #create
            return 1

        #update
        print("--- UPDATE ----")
        dto.mergeForUpdateAgenda(existent)
        # map contact to agendaProDto
        print(dto)
        print("--------------- RECORD")

    @staticmethod
    def test_some(record):
        print("909090909090900909090")
        print(record.description)