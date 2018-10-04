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
# limitations under the License.

import pyVmomi


def collect(content, type, properties, ids):
    """
    Leverage the Property Collector to retrieve properties from any
    Managed Object.

    Args:
    - content: service instance content
    - type: object type
    - properties: optional array of properties to get (default: all)
    - ids: optional array of MOIDs to limit results (default: all)

    Returns:
    - dict: key = moid, value = dict of properties
    """

    vimtype = getattr(pyVmomi.vim, type)

    rootFolder = content.rootFolder
    viewMgr = content.viewManager
    if not ids:
        view = viewMgr.CreateContainerView(container=rootFolder,
                                           type=[vimtype],
                                           recursive=True)
    else:
        view = viewMgr.CreateListView()
        for id in ids:
            view.ModifyListView(add=[\
                pyVmomi.VmomiSupport.GetWsdlType('urn:vim25', type)(id)])

    collector = content.propertyCollector
    traversal_spec = pyVmomi.vmodl.query.PropertyCollector.TraversalSpec()
    traversal_spec.name = 'traverseEntities'
    traversal_spec.path = 'view'
    traversal_spec.skip = False
    traversal_spec.type = view.__class__

    obj_spec = pyVmomi.vmodl.query.PropertyCollector.ObjectSpec()
    obj_spec.obj = view
    obj_spec.skip = True
    obj_spec.selectSet = [traversal_spec]

    property_spec = pyVmomi.vmodl.query.PropertyCollector.PropertySpec()
    property_spec.type = vimtype
    if not properties:
        property_spec.all = True
    else:
        property_spec.pathSet = properties

    filter_spec = pyVmomi.vmodl.query.PropertyCollector.FilterSpec()
    filter_spec.objectSet = [obj_spec]
    filter_spec.propSet = [property_spec]

    raw = collector.RetrieveContents([filter_spec])

#
# The general format for what is returned from the property collector:
#
# {
#  'status':None,
#  'result':(vmodl.query.PropertyCollector.ObjectContent)   [
#     (vmodl.query.PropertyCollector.ObjectContent)      {
#        dynamicType = <unset>,
#        dynamicProperty = (vmodl.DynamicProperty)         [
#
#        ],
#        obj = 'vim.VirtualMachine:vm-45',
#        propSet = (vmodl.DynamicProperty)         [
#           (vmodl.DynamicProperty)            {
#              name = u'config.hardware.memoryMB',
#              val = 4096
#           }
#        ],
#        missingSet = (vmodl.query.PropertyCollector.MissingProperty)         [
#
#        ]
#     }
#  ]
# }
#
# We want to convert this into:
#
# {
#   "vm-45": {
#     "config.hardware.memoryMB": 4096
#   }
# }
#

    found = False
    result = {}
    for object in raw:
        objid = unquote(object.obj).split(':')[-1]
        ps = {}
        for property in object.propSet:
            ps[unquote(property.name)] = property.val
            Found = True
        result[objid] = ps
    return (Found, result)


def unquote(quoted):
    return str(quoted).strip("'")
