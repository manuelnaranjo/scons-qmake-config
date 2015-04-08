# -*- coding: utf-8 -*-

# A SCons tool to simplify pkg-config usage on SCons
#
# Copyright (c) 2015 Naranjo Manuel Francisco < naranjo dot manuel at gmail dot com >
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import tempfile
import subprocess

from functools import partial

def exists(env):
    # we suppose the tool is always available
    return True

def QmakeSupported(context):
    text = 'Checking for ${QMAKE_BIN}... '
    instruction = '${QMAKE_BIN} --version'

    context.Message(context.env.subst(text))
    ret = context.TryAction(instruction)[0]
    context.Result(ret == 1)
    return ret == 1

TEMPLATE = '''
CONFIG -= qt
CONFIG += release
CONFIG += %(name)s

%(extra)s
'''

def prepareQmake(name, extra=None):
    pro = tempfile.NamedTemporaryFile(suffix='.pro')
    out = tempfile.NamedTemporaryFile('rw+')

    pro.write(TEMPLATE % {'name': name, 'extra': extra or ''})
    pro.flush()
    line = '${QMAKE_BIN} -o %s -nodepend %s' % (out.name, pro.name)

    return pro, out ,line

def QmakeCheck(context, name, extra=None):
    context.Message('Checking for %s... ' % name)

    pro, out, line = prepareQmake(name, extra)
    ret = context.TryAction(line)[0]
    pro.close()
    out.close()

    context.Result(ret == 1)
    return ret

def RunQmakeExtractFlags(env, name, flags = None):
    pro, out, line = prepareQmake(name)
    line = env.subst(line)
    ret = subprocess.check_call(line, shell=True)

    makefile = out.read()
    pro.close()
    out.close()

    if flags is None:
        flags = ['DEFINES', 'INCPATH', 'LIBS']

    out = {}
    values = ''
    for line in makefile.split('\n'):
        if '=' not in line:
            continue
        label, value = line.split('=')
        label = label.strip()
        if label in flags:
            value = value.replace('$(SUBLIBS)', '').replace('-I.', '')
            values = values + ' ' + value

    out.update(env.ParseFlags(values))

    for key, val in list(out.iteritems()):
        if len(out[key]) == 0:
            out.pop(key)

    return out

def QmakeGetLibs(env, name, modifyenv = True):
    out = RunQmakeExtractFlags(env, name, ['LIBS'])
    if modifyenv:
        env.AppendUnique(**out)
    return out

def QmakeGetCflags(env, name, modifyenv = True):
    out = RunQmakeExtractFlags(env, name, ['DEFINES', 'INCPATH'])
    if modifyenv:
        env.AppendUnique(**out)
    return out

def QmakeGetAllFlags(env, name, modifyenv = True):
    out = RunQmakeExtractFlags(env, name)
    if modifyenv:
        env.AppendUnique(**out)
    return out

def generate(env):
    from SCons import SConf
    SConfBase = SConf.SConfBase

    if not env.has_key('QMAKE_BIN'):
        env['QMAKE_BIN'] = 'qmake'

    class QmakeSConfBase(SConfBase):
        def __init__(self, env, custom_tests = {}, *a, **kw):
            qmake_tests = {
                'QmakeSupported': QmakeSupported,
                'QmakeCheck': QmakeCheck
            }
            qmake_tests.update(custom_tests)
            SConfBase.__init__(self, env, qmake_tests, *a, **kw)

    setattr(SConf, 'SConfBase', QmakeSConfBase)
    env.AddMethod(QmakeGetLibs)
    env.AddMethod(QmakeGetCflags)
    env.AddMethod(QmakeGetAllFlags)
