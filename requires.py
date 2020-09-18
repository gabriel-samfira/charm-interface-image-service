# Copyright 2020 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from charms.reactive import RelationBase
from charms.reactive import hook
from charms.reactive import scopes


class ImageServiceRequires(RelationBase):
    scope = scopes.GLOBAL

    # These remote data fields will be automatically mapped to accessors
    # with a basic documentation string provided.

    auto_accessors = [
            'glance-api-ready',
            'glance-enabled-backends',
            'glance-api-server']

    @hook('{requires:baremetal}-relation-joined')
    def joined(self):
        self.set_state('{relation_name}.connected')
        self.update_state()

    def update_state(self):
        if self.data_complete():
            self.remove_state('{relation_name}.departed')
            self.set_state('{relation_name}.available')
        else:
            self.remove_state('{relation_name}.available')

    @hook('{requires:baremetal}-relation-changed')
    def changed(self):
        self.update_state()

    @hook('{requires:baremetal}-relation-{broken,departed}')
    def departed(self):
        self.remove_state('{relation_name}.available')
        self.set_state('{relation_name}.departed')

    def enabled_backends(self):
        backends = self.glance_enabled_backends()
        if not backends:
            return []
        return backends.replace(' ', '').split(',')

    def enabled_backend_types(self):
        backend_types = []
        backends = self.enabled_backends()
        for be in backends:
            be_pair = be.split(":")
            if len(be_pair) != 2:
                # enabled_backends should be of the form
                # <backend_name>:<backend_type>. Ignore invalid backends.
                continue
            backend_types.append(be_pair[1])
        return backend_types

    def data_complete(self):
        data = {
            "api_ready": self.glance_api_ready(),
            "enabled_backends": self.glance_enabled_backends(),
            "api_server": self.glance_api_server()
        }
        return all(data.values())

