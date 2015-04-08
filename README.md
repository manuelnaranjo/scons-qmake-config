# About

This is a [SCons](http://www.scons.org) tool that helps working with
qmake if the host os supports it, allowing to get configuration issues provided
by qmake features and projects.

# Installation

You will need to clone this Git repository and then possibly additionally
provide some links. SCons has a number of ways of adding new tools depending
on whether you want them available only for a single project, for all the
projects of an individual user, or for all projects on a given system. The
location to which the clone should be made depends on which of these
situations you want to support.

Whichever location you choose the command will be:

    $ git clone https://github.com/manuelnaranjo/scons-qmake-config.git qmake-config

The name of the target directory will become the name of the tool for your
situation. In this case _qmake-config_ is the target directory name and hence
_qmake-config_ will be the name of the tool.

# Usage

Currently there are a few methods provided by this tool, in any case you first
need to initialize the tool

    e = Environment(tools=['qmake-config'])

Another alternative is

    e = Environment(...)
    ...
    e.Tool('qmake-config')

Now you you will find two new methods in the Configure environment:
_QmakeSupported_ and _QmakeCheck_, also three methods are provided in
the caller environment _QmakeGetLibs_, _QmakeGetCflags_ and _QmakeGetAllFlags_.

## Configure methods

### QmakeSupported

This method allows testing if qmake is supported in the current environment

    e = Environment(tools=[qmake-config'])
    c = e.Configure()
    if c.QmakeSupported():
        print 'qmake supported'
    ...
    c.Finish()

### QmakeCheck

This method checks if a library is provided by qmake.

    ...
    if c.QmakeCheck('qwt'):
        print 'qwt provided'
    ...

### QmakeGetLibs

This method allows to get the flags related to library provided by qmake

    ...
    # the environment will get modified with the flags provided by qmake
    e.QmakeGetLibs('qwt')

    # if you don't want the calling environment to be modify you can do this
    flags = e.QmakeGetLibs('qwt', modifyenv=False)
    # now flags is a dictionary with the parsed flags
    e.AppendUnique(**flags)
    ...

### QmakeGetCflags

Same as _QmakeGetLibs_ but will provide the values associated with c compiler.

### QmakeGetAllFlags

Combines the results of _QmakeGetLibs_ and _QmakeGetCflags_

## Cross-compiling

Cross-compiling hasn't been tested yet, but an environment variable has been
defined to allow the user of the tool to specify the name of the qmake
tool to use, set variable _QMAKE\_BIN_ to the desired value.
