#!/usr/bin/python
class FilterModule(object):
    def filters(self):
        'Define filters'
        return {
            'removesensitive': self.removesensitive,
        }

    def removesensitive(self, data, key_to_remove='password'):
        """ If data contains password it will change to SECRETE """
        for value in data:
            if key_to_remove in value['item']:
                value['item'][key_to_remove] = "******"
        return data
