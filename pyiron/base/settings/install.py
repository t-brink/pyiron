# coding: utf-8
# Copyright (c) Max-Planck-Institut für Eisenforschung GmbH - Computational Materials Design (CM) Department
# Distributed under the terms of "New BSD License", see the LICENSE file.

import os
import getopt
from zipfile import ZipFile
from shutil import copytree, rmtree
import tempfile
import stat
import sys

if sys.version_info >= (3,):
    import urllib.request as urllib2
else:
    import urllib as urllib2

__author__ = "Jan Janssen"
__copyright__ = "Copyright 2019, Max-Planck-Institut für Eisenforschung GmbH - " \
                "Computational Materials Design (CM) Department"
__version__ = "1.0"
__maintainer__ = "Jan Janssen"
__email__ = "janssen@mpie.de"
__status__ = "production"
__date__ = "Sep 1, 2017"


def _download_resources(zip_file="resources.zip",
                        resource_directory="~/pyiron/resources",
                        giturl_for_zip_file="https://github.com/pyiron/pyiron-resources/archive/master.zip",
                        git_folder_name="pyiron-resources-master"):
    """
    Download pyiron resources from Github

    Args:
        zip_file (str): name of the compressed file
        resource_directory (str): directory where to extract the resources - the users resource directory
        giturl_for_zip_file (str): url for the zipped resources file on github
        git_folder_name (str): name of the extracted folder

    """
    user_directory = os.path.normpath(os.path.abspath(os.path.expanduser(resource_directory)))
    temp_directory = tempfile.gettempdir()
    temp_zip_file = os.path.join(temp_directory, zip_file)
    temp_extract_folder = os.path.join(temp_directory, git_folder_name)
    urllib2.urlretrieve(giturl_for_zip_file, temp_zip_file)
    if os.path.exists(user_directory):
        raise ValueError('The resource directory exists already, therefore it can not be created: ', user_directory)
    with ZipFile(temp_zip_file) as zip_file_object:
        zip_file_object.extractall(temp_directory)
    copytree(temp_extract_folder, user_directory)
    if os.name != 'nt':  #
        for root, dirs, files in os.walk(user_directory):
            for file in files:
                if '.sh' in file:
                    st = os.stat(os.path.join(root, file))
                    os.chmod(os.path.join(root, file), st.st_mode | stat.S_IEXEC)
    os.remove(temp_zip_file)
    rmtree(temp_extract_folder)


def _write_config_file(file_name='~/.pyiron', project_path='~/pyiron/projects', resource_path='~/pyiron/resources'):
    """
    Write configuration file and create the corresponding project path.

    Args:
        file_name (str): configuration file name - usually ~/.pyiron
        project_path (str): the location where pyiron is going to store the pyiron projects
        resource_path (str): the location where the resouces (executables, potentials, ...) for pyiron are stored.
    """
    config_file   = os.path.normpath(os.path.abspath(os.path.expanduser(file_name)))
    project_path  = os.path.normpath(os.path.abspath(os.path.expanduser(project_path)))
    resource_path = os.path.normpath(os.path.abspath(os.path.expanduser(resource_path)))

    if not os.path.exists(project_path):
        os.makedirs(project_path)

    if not os.path.isfile(config_file):
        with open(config_file, 'w') as cf:
            cf.writelines(['[DEFAULT]\n',
                           'PROJECT_PATHS = ' + project_path + '\n',
                           'RESOURCE_PATHS = ' + resource_path + '\n'])

def _write_environ_var(config_file_name='~/.pyiron'):
    config_file = os.path.normpath(os.path.abspath(os.path.expanduser(config_file_name)))

    # Check whether bashrc already contains PYIRONCONFIG, this can happen in bashrc has not been sourced yet
    with open(os.path.expanduser("~/.bashrc"), "r") as outfile:
        lines = outfile.readlines()
    if not any(['PYIRONCONFIG' in line for line in lines]):
        # Write to bashrc
        with open(os.path.expanduser("~/.bashrc"), "a") as outfile:
            if not lines[-1]=='\n': outfile.write('\n')
            outfile.write("# PYIRONCONFIG for pyiron config file location\n")
            outfile.write("export PYIRONCONFIG={}\n".format(config_file))
        print('Please source the .bashrc after the initial configuration or reset your terminal.')
        print('')
        print('$ source ~/.bashrc')
    else:
        raise SystemError('Your .bashrc has the correct environment variable but has not been sourced. Please execute the following in your bash shell: source ~/.bashrc')



def install_pyiron(config_file_name='~/.pyiron',
                   zip_file="resources.zip",
                   project_path='~/pyiron/projects',
                   resource_directory="~/pyiron/resources",
                   giturl_for_zip_file="https://github.com/pyiron/pyiron-resources/archive/master.zip",
                   git_folder_name="pyiron-resources-master"):
    """
    Function to configure the pyiron installation.

    Args:
        config_file_name (str): configuration file name - usually ~/.pyiron
        zip_file (str): name of the compressed file
        project_path (str): the location where pyiron is going to store the pyiron projects
        resource_directory (str): the location where the resouces (executables, potentials, ...) for pyiron are stored.
        giturl_for_zip_file (str): url for the zipped resources file on github
        git_folder_name (str): name of the extracted folder
    """
    # Build directories if install_pyiron has been skipped for custom pyiron config file
    _write_config_file(file_name=config_file_name, project_path=project_path, resource_path=resource_directory)
    _write_environ_var(config_file_name=config_file_name)
    _download_resources(zip_file=zip_file,
                        resource_directory=resource_directory,
                        giturl_for_zip_file=giturl_for_zip_file,
                        git_folder_name=git_folder_name)


def command_line(argv):
    """
    Parse the command line arguments.

    Args:
        argv: Command line arguments

    """
    config_file_name = '~/.pyiron'
    zip_file = "resources.zip"
    resource_path = "~/pyiron/resources"
    project_path = "~/pyiron/projects"
    giturl_for_zip_file = "https://github.com/pyiron/pyiron-resources/archive/master.zip"
    git_folder_name = "pyiron-resources-master"
    try:
        opts, args = getopt.getopt(argv, "c:r:u:p:h", ["config=", "resource_path=", "project_path=", "url="])
    except getopt.GetoptError:
        print('install.py -c <config_file> -p <project_path> -r <resource_dir> -u <url>')
        sys.exit()
    else:
        for opt, arg in opts:
            if opt in ("-h", "--help"):
                print('install.py -c <config_file> -p <project_path> -r <resource_dir> -u <url>')
                sys.exit()
            elif opt in ("-c", "--config"):
                config_file_name = arg
            elif opt in ("-r", "--resource_path"):
                resource_path = arg
            elif opt in ("-p", "--project_path"):
                project_path = arg
            elif opt in ("-u", "--url"):
                giturl_for_zip_file = arg
        install_pyiron(config_file_name=config_file_name,
                       zip_file=zip_file,
                       project_path=project_path,
                       resource_directory=resource_path,
                       giturl_for_zip_file=giturl_for_zip_file,
                       git_folder_name=git_folder_name)


if __name__ == "__main__":
    command_line(sys.argv[1:])
