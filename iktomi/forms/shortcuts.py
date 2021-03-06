# -*- coding: utf-8 -*-

from . import convs, widgets, fields
from ..utils import N_


class PasswordConv(convs.Char):

    error_mismatch = N_('password and confirm mismatch')
    error_required = N_('password required')

    def from_python(self, value):
        return dict([(field.name, None) for field in self.field.fields])

    def get_initial(self):
        return ''

    def to_python(self, value):
        etalon = value[list(value)[0]]
        for field in self.field.fields:
            self.assert_(value[field.name] == etalon,
                         self.error_mismatch)
        self.assert_(etalon not in (None, '')  or self.required,
                     self.error_required)
        return etalon


def PasswordSet(name='password',
                 min_length=3, max_length=200, required=False,
                 password_label=None, confirm_label='confirmmm',
                 **kwargs):
        # class implementation has problem with Fieldset copying:
        # it requires to save all kwargs in object's __dict__
        char = convs.Char(convs.limit(min_length, max_length),
                          required=required)
        items = (('pass', password_label), ('conf', confirm_label))
        
        kwargs['fields'] = [fields.Field(subfieldname,
                                         conv=char,
                                         label=label,
                                         widget=widgets.PasswordInput)
                            for subfieldname, label in items]
        kwargs.setdefault('conv', PasswordConv(required=required))
        kwargs.setdefault('template', 'fieldset-line')
        
        return fields.FieldSet(name, get_initial=lambda: '', **kwargs)

