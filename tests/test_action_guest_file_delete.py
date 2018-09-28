# Licensed to the StackStorm, Inc ('StackStorm') under one or more
# contributor license agreements.  See the NOTICE file distributed with
# this work for additional information regarding copyright ownership.
# The ASF licenses this file to You under the Apache License, Version 2.0
# (the "License"); you may not use this file except in compliance with
# the License.  You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and

import mock
from vsphere_base_action_test_case import VsphereBaseActionTestCase
from guest_file_delete import DeleteFileInGuest

__all__ = [
    'DeleteFileInGuestTestCase'
]


class DeleteFileInGuestTestCase(VsphereBaseActionTestCase):
    __test__ = True
    action_cls = DeleteFileInGuest

    def test_normal(self):
        # test with and without guest_directory:
        for vars in [(None, '/tmp/foo.txt'), ('/tmp', 'foo.txt')]:
            (action, mock_vm) = self.mock_one_vm('vm-12345')
            mockFileMgr = mock.Mock()
            mockFileMgr.DeleteFileInGuest = mock.Mock()
            action.si_content.guestOperationsManager = mock.Mock()
            action.si_content.guestOperationsManager.fileManager = mockFileMgr
            result = action.run(vm_id='vm-12345', username='u', password='p',
                                guest_directory=vars[0], guest_file=vars[1])
            mockFileMgr.DeleteFileInGuest.assert_called_once_with(
                mock.ANY, mock.ANY, '/tmp/foo.txt')
            self.assertEqual(result, None)
