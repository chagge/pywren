import base64
import copy
try:
    import cPickle as pickle
except:
    import pickle
try:
    from cStringIO import StringIO
except:
    import StringIO

from functools import partial
import inspect
import numbers
import socket
import subprocess
import time
import logging

from cloudpickle import CloudPickler
from module_dependency import ModuleDependencyAnalyzer
import preinstalls

class Serialize(object):
    def __init__(self):
        
        self._modulemgr = ModuleDependencyAnalyzer()
        preinstalled_modules = [name for name, _ in preinstalls.modules]
        self._modulemgr.ignore(preinstalled_modules)


    def __call__(self, f, *args, **kwargs):
        """
        Serialize 
        """
        
        f_kwargs = {}
        for k, v in kwargs.items():
            if not k.startswith('_'):
                f_kwargs[k] = v
                del kwargs[k]
        
        s = StringIO()
        cp = CloudPickler(s, 2)
        cp.dump((f, args, f_kwargs))
        
        if '_ignore_module_dependencies' in kwargs:
            ignore_modulemgr = kwargs['_ignore_module_dependencies']
            del kwargs['_ignore_module_dependencies']
        else:
            ignore_modulemgr = False
            
        if not ignore_modulemgr:
            # Add modules
            for module in cp.modules:
                self._modulemgr.add(module.__name__)
            
            mod_paths = self._modulemgr.get_and_clear_paths()
            print "mod_paths=", mod_paths
        return cp, mod_paths
        #     vol_name = self._get_auto_module_volume_name()
        # if self._modulemgr.has_module_dependencies:
        #         v = self.multyvac.volume.get(vol_name)
        #         if not v:
        #             try:
        #                 self.multyvac.volume.create(vol_name, '/pymodules')
        #             except RequestError as e:
        #                 if 'name already exists' not in e.message:
        #                     raise
        #             v = self.multyvac.volume.get(vol_name)
        #         if mod_paths:
        #             v.sync_up(mod_paths, '')
            
        # kwargs['_stdin'] = s.getvalue()
        # kwargs['_result_source'] = 'file:/tmp/.result'
        # kwargs['_result_type'] = 'pickle'
        # if not ignore_modulemgr and self._modulemgr.has_module_dependencies:
        #     kwargs.setdefault('_vol', []).append(vol_name)
        # # Add to the PYTHONPATH if user is using it as well
        # env = kwargs.setdefault('_env', {})
        # if env.get('PYTHONPATH'):
        #     env['PYTHONPATH'] = env['PYTHONPATH'] + ':/pymodules'
        # else:
        #     env['PYTHONPATH'] = '/pymodules'
            
        # tags = kwargs.setdefault('_tags', {})
        # # Make sure function name fits within length limit for tags
        # fname = JobModule._func_name(f)
        # if len(fname) > 100:
        #     fname = fname[:97] + '...'
        # tags['fname'] = fname
        
        # return self.shell_submit(
        #     'python -m multyvacinit.pybootstrap',
        #     **kwargs
        # )
if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    mda = ModuleDependencyAnalyzer()


    import testmod

    serialize = Serialize()

    def foo(x):
        y = testmod.bar_square(x)
        return y + 1

    p =  serialize(foo, 7)
    print p.modules