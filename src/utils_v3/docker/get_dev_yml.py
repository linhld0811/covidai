#!/usr/bin/env python3

# Copyright 2020 (author: lamnt45)


DIRECTION='''
This script run the following steps:
-   Parse .env file to list all .YMLs (docker-compose files)
-   For each .YML file, list all services
-   For each service, look into its Dockerfile (if available),
    expand all variables (ARGS + ENV)
-   Look into "expanded" Dockerfile and look for all ADD/COPY instruction
    to guess the mountings.

For simplicity's sake, use will have to manually double check
the generated file for undesirable overrides
'''


# common
import os
import argparse, textwrap
import traceback


# technical
import glob
import json, yaml
import shutil
import tempfile
import uuid


# logger
from ..logger import getLogger
logger = getLogger(__name__)


# dockerfile parsing
import dockerfile_parse


# gitignore
from gitignore_parser import parse_gitignore
GitIgnore_Matcher = parse_gitignore('./.gitignore')


# mktemp
from ..easy_basher import *
from ..common import *
from ..file_based_db import *


# envs
Configs = {
    'env_file'     : '.env',
    'exp_dir'      : mktemp(__file__),
}

Configs.update({

    'COMPOSE_PATH_SEPARATOR' : get_shell_var_value(
        Configs['env_file'],
        'COMPOSE_PATH_SEPARATOR',
    ),

    'COMPOSE_FILE'           : get_shell_var_value(
        Configs['env_file'],
        'COMPOSE_FILE',
    ),

    'COMPOSE_DEV_FILE' : get_shell_var_value(
        Configs['env_file'],
        'COMPOSE_DEV_FILE',
    ),

    'BUILD_REQUIRING_SERVICES' : get_shell_var_value(
        Configs['env_file'],
        'BUILD_REQUIRING_SERVICES',
    ),
})


def get_args():
    parser = argparse.ArgumentParser(
        description=textwrap.dedent(DIRECTION),
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('-a', type=str, default='',
                        help='''Always mounted (e.g: "./exp:/exp ./tmp:/tmp''')

    args = parser.parse_args()

    return args


def has_envs_expanded(file, env_file):

    new_file = slugify_uniquify_filename(
            os.path.join(
                Configs['exp_dir'],
                os.path.basename(file),
            )
        )

    bash(r'''
        for i in $(env | /usr/bin/awk -F"=" '{{print $1}}') ; do unset $i ; done
        set -a; . {0}; set +a
        /usr/bin/envsubst <"{1}" >"{2}"

    '''.format(
        env_file,
        file,
        new_file,
    ), silent=True)

    return new_file


def main():

    # stage 0
    args = get_args()

    # stage 1
    logger.green('### Getting Compose_Files (and expand variables)')

    recreate(
        Configs['exp_dir']
    )

    Files = {
        '.ignore' : Configs['exp_dir'] + os.sep + '.ignore'
    }

    Compose_Overlaying_Files = Configs['COMPOSE_DEV_FILE'].split('\n')
    Compose_Files = [ f for f in Compose_Overlaying_Files if f.count('.yml') > 0 ]

    Compose_Files = Configs['COMPOSE_FILE'].split('\n')
    Compose_Files = [ f for f in Compose_Files if f.count('.yml') > 0 and f not in Compose_Overlaying_Files ]


    ComposeFile_2_ExpandedComposeFile = {}
    for file in Compose_Files:
        ComposeFile_2_ExpandedComposeFile[file] = has_envs_expanded(file, Configs['env_file'])


    # stage 2
    logger.green('### Getting Service_2_Dockerfile / Service_2_Args')

    COMPOSE_VERSION = None

    Service_2_Dockerfile = {}
    Service_2_Args = {}
    Service_2_Mountings = {}
    ComposeFile_2_Services = {}
    for compose_file, expanded_compose_file in ComposeFile_2_ExpandedComposeFile.items():

        logger.green('expanded_compose_file:', expanded_compose_file)

        with open(expanded_compose_file, 'r') as f:
            Compose_File_Content = yaml.load(f)

            if 'version' in Compose_File_Content and not COMPOSE_VERSION:
                COMPOSE_VERSION = Compose_File_Content['version']

            if 'services' in Compose_File_Content:
                for service, Service_Configs in Compose_File_Content['services'].items():

                    if service not in Configs['BUILD_REQUIRING_SERVICES']:

                        logger.green('service:', service)

                        # stage 0
                        if 'build' in Service_Configs:

                            if 'dockerfile' in Service_Configs['build']:
                                Service_2_Dockerfile[service] = Service_Configs['build']['dockerfile']

                            if 'args' in Service_Configs['build']:
                                Service_2_Args[service] = Service_Configs['build']['args']

                        # stage 1
                        Service_2_Mountings[service] = []

                        if 'volumes' in Service_Configs:

                            for x in Service_Configs['volumes']:
                                host_dir, cont_dir = x.split(':')[0:2]
                                mounting = [
                                    host_dir.rstrip(os.sep),
                                    cont_dir.rstrip(os.sep),
                                ]
                                Service_2_Mountings[service].append(mounting)

                        # stage 2
                        if compose_file not in ComposeFile_2_Services:
                            ComposeFile_2_Services[compose_file] = []

                        ComposeFile_2_Services[compose_file].append(service)

    logger.green('Service_2_Dockerfile:', Service_2_Dockerfile)
    logger.green('Service_2_Args:', Service_2_Args)
    logger.green('Service_2_Mountings:', Service_2_Mountings)
    logger.green('ComposeFile_2_Services:', ComposeFile_2_Services)


    # stage 3
    logger.green('### Expanding variables for Service_2_Dockerfile')
    for service, docker_file in Service_2_Dockerfile.items():

        service_args_file = slugify_uniquify_filename(
            os.path.join(
                Configs['exp_dir'],
                service + '.args',
            )
        )

        shutil.copy(
            Configs['env_file'],
            service_args_file,
        )

        write_list_to_file(
            Service_2_Args[service],
            service_args_file,
            mode='a'
        )

        Service_2_Dockerfile[service] = has_envs_expanded(docker_file, service_args_file)

    logger.green('Service_2_Dockerfile', Service_2_Dockerfile)


    # stage 4
    logger.green('### Getting mount points')

    bash(r'''
        echo -e "\n" \
            | cat "{0}" - "{1}" > "{2}"
    '''.format(
        '.gitignore',
        '.dockerignore',
        Files['.ignore']
    ))

    Service_2_Dev_Mountings = {}

    for service, Dockerfile in Service_2_Dockerfile.items():

        # stage 4.0
        Service_2_Dev_Mountings[service] = []

        logger.green('\nservice:', service)

        dfp = dockerfile_parse.DockerfileParser(
            fileobj=open(Dockerfile, 'rb')
        )

        work_dir = '/'

        # stage 4.1
        for Ins in dfp.structure:

            if Ins['instruction'] in ['WORKDIR']:
                work_dir = Ins['value']

            if Ins['instruction'] in ['ADD', 'COPY']:
                host_node, cont_node = Ins['value'].split()

                host_node = './' + host_node.rstrip('./')

                cont_node = os.path.join(
                    work_dir,
                    cont_node
                )
                cont_node__dirname, cont_node__basename = os.path.split(cont_node)
                if cont_node__basename == '.' :
                    cont_node = os.path.join(
                        cont_node__dirname,
                        os.path.basename(host_node),
                    )

                Service_2_Dev_Mountings[service].append(
                    [host_node, cont_node]
                )

        # stage 4.2
        if len(Service_2_Dev_Mountings[service]) == 0:
            del Service_2_Dev_Mountings[service]
            continue

        Service_2_Dev_Mountings[service] = sorted(
            Service_2_Dev_Mountings[service],
            key = lambda x: (x[1], x[0]),
        )

        # stage 4.3
        S2D = Service_2_Dev_Mountings[service]
        New_S2D = S2D[:]
        for i in range(len(S2D)):
            for j in range(i+1, len(S2D)):

                if  os.path.isdir(S2D[i][0]) \
                and os.path.isdir(S2D[j][0]) :

                    if S2D[j][1].startswith(S2D[i][1]) :
                        logger.green('Potential overriding detected!')

                        for k in [i,j]:
                            New_S2D[k] = []
                            for f in os.listdir(S2D[k][0]):

                                if not GitIgnore_Matcher(
                                    os.path.join(S2D[k][0], f)
                                ):

                                    New_S2D[k].append([
                                        os.path.join(S2D[k][0], f),
                                        os.path.join(S2D[k][1], f),
                                    ])

        # stage 4.4
        S2D = []
        for i in range(len(New_S2D)):
            if type(New_S2D[i][0]) is list:
                S2D += New_S2D[i]
            else:
                S2D.append(New_S2D[i])

        # stage 4.5
        if args.a :
            S2D += [ x.split(':') for x in args.a.split() ]

        # stage 4.6
        Service_2_Dev_Mountings[service] = sorted(
           list(
                set(tuple(row) for row in S2D)
                - set(tuple(row) for row in Service_2_Mountings[service])
            ),
            key = lambda x: (x[1], x[0]),
        )

    logger.green('Service_2_Dev_Mountings:', Service_2_Dev_Mountings)

    # stage 5
    logger.green('### Getting overlaying compose file content')
    for compose_file, Services in ComposeFile_2_Services.items():

        # stage 0
        compose_file_Splittext = os.path.splitext(compose_file)
        new_compose_file = compose_file_Splittext[0] + '.dev' + compose_file_Splittext[1]

        New_Compose_File_Content = {
            'version' : COMPOSE_VERSION,
            'services' : {},
        }

        for service in Services:
            if service in Service_2_Dev_Mountings:
                New_Compose_File_Content['services'][service] = {
                    'volumes' : [
                        '{}:{}'.format(x[0],x[1]) for x in Service_2_Dev_Mountings[service]
                    ],
                }

        YAML_Content = yaml.dump(
            New_Compose_File_Content,
            default_flow_style=False,
            sort_keys=False
        )

        # perform a quick format
        YAML_Content_Reformatted = ''
        for line in YAML_Content.split('\n'):

            line_stripped = line.strip()
            if  line_stripped:
                if  line_stripped[-1] == ':' \
                    and line_stripped != 'volumes:' :
                    YAML_Content_Reformatted += '\n\n'

            YAML_Content_Reformatted += line + '\n'

        # write to file
        archive(new_compose_file)
        with open(new_compose_file, 'w+') as f:
            f.write(YAML_Content_Reformatted)
            logger.green('Written to:', new_compose_file)


if __name__ == '__main__' :
    try:
        main()
    except Exception as e:
        traceback.print_exc()
        logger.error(e)
    finally:
        logger.green('### Cleaning-up')
        shutil.rmtree(Configs['exp_dir'])
