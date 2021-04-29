#!/usr/bin/env python3

import sys
import os
import getopt
import subprocess
import glob
import types
import importlib.machinery
import importlib.util
import shutil

global run_flag, verbose, norun

run_flag = True
verbose = False
norun = False

def err_exit(str):
        ''' print the error string and exit '''
        print(str)
        sys.exit(1)

def find_file(fn, t):
        ''' Find the first file matching the arg value '''
        f = os.path.splitext(fn)
        if f[1] == t:
            fn = f[0]
        for f in file_list('cfg', t):
                b = os.path.basename(f)
                if os.path.splitext(b)[0] == fn:
                        return f
        return None

def mk_tuple(lst, s):
        ''' Convert a string to a tuple if needed '''
        t = {}

        if type(lst[s]) != tuple:
                if verbose:
                        print('Not a Tuple', type(lst[s]), lst[s])
                t[s] = tuple([lst[s],])
        else:
                if verbose:
                        print('A tuple', type(lst[s]), lst[s])
                t[s] = lst[s]

        if verbose:
                print('New t[s]', type(t[s]), t[s])

        return t[s]

def add_ld_options(s, arg_list):
        ''' Append LD_LIBRARY_PATH option to arg list '''
        if s in cfg.run:
            str = 'LD_LIBRARY_PATH=.'
            for a in mk_tuple(cfg.run, s):
                _p = a % globals()
                str = str + ':' + _p
            arg_list.append(str)

def add_run_options(s, arg_list, p):
        ''' Append options to arg list '''
        if s in cfg.run:
            for a in mk_tuple(cfg.run, s):
                if p is not None:
                    arg_list.append(p)

                _p = a % globals()
                arg_list.append(_p)

def add_setup_options(s, arg_list):
        ''' Append options to arg list '''
        if s in cfg.setup:
                for a in mk_tuple(cfg.setup, s):
                        arg_list.extend(a.split(' '))

def file_list(directory, file_extension):
        ''' Return list of configuration files '''
        fileiter = (os.path.join(root, f)
                for root, _, files in os.walk(directory)
                        for f in files)
        return (f for f in fileiter if os.path.splitext(f)[1] == file_extension)

def load_cfg(fname):
        ''' Load the configuration or .cfg file as a python data file '''

        if not os.path.exists(fname):
                err_exit("Config file %s does not exists\n" % fname)

        try:
                configuration_file = open(fname)
        except:
                err_exit("Error: unable to open file %s\n" % fname)

        global cfg
        loader = importlib.machinery.SourceFileLoader('cfg', fname)
        spec = importlib.util.spec_from_loader(loader.name, loader)
        cfg = importlib.util.module_from_spec(spec)
        loader.exec_module(cfg)
        #print(cfg)

        configuration_file.close()
        shutil.rmtree('Pktgen-DPDK/cfg/__pycache__')

        return cfg

def show_configs():
        ''' Show configuration files '''

        print("Configurations:")
        print("   %-16s - %s" % ("Name", "Description"))
        print("   %-16s   %s" % ("----", "-----------"))

        for fname in file_list('cfg', '.cfg'):
                base = os.path.splitext(os.path.basename(fname))[0]

                try:
                        cfg = load_cfg(fname)

                        if not cfg.description:
                                cfg.description = ""
                        print("   %-16s - %s" % (base, cfg.description))
                except NameError:
                        sys.stderr.write("We were unable to load the module " + fname + \
                        " If you do not plan to use this module you can safely ignore this " \
                        "message.\n")
                finally:
                        # reset the descriptoin to empty, for next loop/file
                        cfg.description = ""

        sys.exit(0)

def parse_configuration(cfg_file):
        ''' Run the configuration in the .cfg file '''

        cfg = load_cfg(cfg_file)

        args = []

        add_run_options('exec', args, None)

        add_ld_options('ld_path', args)

        if not 'app_path' in cfg.run:
                err_exit("'app_path' variable is missing from cfg.run in config file")

        if not 'app_name' in cfg.run:
                err_exit("'app_name' variable is missing from cfg.run in config file")

        # convert the cfg.run['app_name'] into a global variable used in
        # the creation of the applicaiton/path. app_name must be a global variable.
        global app_name
        app_name = cfg.run['app_name']

        # Try all of the different path versions till we find one.
        fname = None
        for app in cfg.run['app_path']:
                fn = app % globals()
                #print("   Trying %s" % fn)
                if os.path.exists(fn):
                        fname = fn
                        if verbose:
                                print("Found %s" % fn)
                        break

#        if not fname:
#                err_exit("Error: Unable to locate application %s" % cfg.run['app_name'])

        args.extend([fname])

        add_run_options('cores', args, '-l')
        add_run_options('nrank', args, '-n')
        add_run_options('proc', args, '--proc-type')
        add_run_options('log', args, '--log-level')
        add_run_options('prefix', args, '--file-prefix')
        add_run_options('shared', args, '-d')
        add_run_options('blocklist', args, '-b')
        add_run_options('allowlist', args, '-a')
        add_run_options('vdev', args, '--vdev')
        add_run_options('plugin', args, '-d')
        args.extend(["--"])
        add_run_options('opts', args, None)
        add_run_options('map', args, '-m')
        add_run_options('pcap', args, '-s')
        add_run_options('theme', args, '-f')
        add_run_options('loadfile', args, '-f')
        add_run_options('logfile', args, '-l')

        # Convert the args list to a single string with spaces.
        str = ""
        for a in args:
                str = str + "%s " % a

        # Output the command line
        # print(str)
        if norun:
                return

        if verbose:
                print("Command line:")
                print(args)

        return str
#parse_configuration("./Pktgen-DPDK/cfg/default.cfg")

