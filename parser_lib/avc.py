#
# Copyright (c) 2018 - present.  Boling Consulting Solutions (bcsw.net)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# http://www.apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from __future__ import (
    absolute_import, division, print_function, unicode_literals
)


class AVC(object):
    """
    Attribute Value Change Notification information.

    Actual attribute numbers start at 1 since the 'Entity ID' is always
    the first attribute (#0) in an ME and it is never covered by an AVC.
    """
    def __init__(self, table):
        # Table number for debug purposes
        self._table_no = table.doc_table_number if table is not None else None
        self._attributes = {
            attr: (False,       # If True, AVC for attribute
                   'N/A'        # Attribute Name
                   '')          # Description
            for attr in range(0, 17)
        }

    def to_dict(self):
        # TODO: Save/restore of table number needed?
        return self._attributes

    @property
    def attributes(self):
        return self._attributes

    @attributes.setter
    def attributes(self, value):
        self._attributes = value

    @staticmethod
    def load(data):
        if len(data) == 0:
            return None

        avc = AVC(None)
        try:
            avc.attributes = {int(index): text for index, text in data.items()}
        except Exception as _e:
            pass
        return avc

    def has_avc(self, attr):
        """
        Does the given attribute have an AVC associated to it?
        :param attr: (int) attribute number
        :return: (bool)
        """
        return self._attributes[attr][0]

    def attribute_name(self, attr):
        return self._attributes[attr][1]

    def attribute_description(self, attr):
        return self._attributes[attr][2]

    @staticmethod
    def create_from_table(table):
        if len(table.rows) == 0:
            return None

        try:
            avc = AVC(table)

            for row in table.rows:
                number = row.get('Number')
                name = row.get('Attribute value change')
                description = row.get('Description')

                try:
                    is_avc = name.strip().lower() not in ('n/a', 'Reserved')
                    if is_avc:
                        value = int(number.strip())
                        assert 1 <= value <= 16, 'Invalid attribute number: {}'.format(value)

                        is_avc = name.strip().lower() not in ('n/a', 'Reserved')
                        avc.attributes[value] = (is_avc,
                                                 name.strip(),
                                                 description.strip())

                except ValueError:  # Expected if of form  n..m
                    # Watch out for commentary text in AVC tables. Often a NOTE at the end
                    if number[:4].lower() == 'note':
                        continue

                    values = number.strip().split('..')
                    for value in range(int(values[0]), int(values[1]) + 1):
                        # NOTE: Attributes are usually 1..16 but ME 329 (vEth Interface Point)
                        #       has an n/a entry coded 0..1
                        assert 0 <= value <= 16, 'Invalid attribute number: {}'.format(value)
                        avc.attributes[value] = (False,
                                                 name.strip(),
                                                 description.strip())
            return avc

        except Exception as e:
            print('Table number parsing error: {}'.format(e))
            return None
