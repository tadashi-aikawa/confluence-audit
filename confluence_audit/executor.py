# -*- coding: utf-8 -*-

"""
Usage:
  confluence_audit [--config=<yaml>]
  confluence_audit permission_list --group=<group> [--config=<yaml>]

Options:
  --config = <yaml>          Configuration file
  --group = <group>          Group name
"""

import os
import sys
from docopt import docopt

from fn import _
from owlmixin import TList, TDict, TOption

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.append(PROJECT_ROOT)
from confluence_audit import __version__
from confluence_audit.apiclient import ApiClient
from confluence_audit.models import SpacePermission, SpacePermissionItem, Config, Violator, Deny, Args

groups_by_member: TDict[TList[str]] = {}


def find_violator(deny: Deny, violator: Violator) -> Violator:
    global groups_by_member

    deny_joined_groups = deny.join_group_names.get_or(TList())
    deny_groups = deny.group_names.get_or(TList())

    return Violator.from_dict({
        'user_names': violator.user_names.filter(
            lambda n: groups_by_member.get(n) and groups_by_member.get(n).any(lambda x: x in deny_joined_groups)
        ),
        'group_names': violator.group_names.filter(lambda n: n in deny_groups),
        'anonymous': deny.anonymous.get_or(False) and violator.anonymous
    })


def find_violator_by_space(space: str, overview: Violator,
                           deny_list: TList[Deny]) -> Violator:
    violators: TList[Violator] = deny_list \
        .reject(lambda d: space in d.excepts.get_or([])) \
        .map(lambda d: find_violator(d, overview))

    # TODO: Control anonymous by option
    return Violator.from_dict({
        'space': space,
        'user_names': violators.flat_map(_.user_names).uniq(),
        'group_names': violators.flat_map(_.group_names).uniq(),
        'anonymous': violators.any(_.anonymous)
    })


def grouping_by_names(space_permissions: TList[SpacePermission]) -> Violator:
    items: TList[SpacePermissionItem] = space_permissions \
        .flat_map(_['permissions']) \
        .flat_map(_.space_permissions)

    return Violator.from_dict({
        'user_names': items.map(_.user_name).map(lambda x: x.get()).filter(_).uniq(),
        'group_names': items.map(_.group_name).map(lambda x: x.get()).filter(_).uniq(),
        'anonymous': items.any(lambda x: x.user_name.is_none() and x.group_name.is_none())
    })


def find_violators(args: Args, config: Config) -> TOption[TList[Violator]]:
    global groups_by_member

    api = ApiClient(config.base_url, os.environ['USER'], os.environ['PASSWORD'])

    groups_by_member = api.fetch_group() \
        .flat_map(lambda g: api.fetch_members(g).map(lambda m: {'member': m, 'group': g})) \
        .group_by(_['member'].username) \
        .map_values(lambda ds: ds.map(_['group'].name))

    violators: TList[Violator] = api.fetch_spaces() \
        .map(_.key) \
        .map(lambda k: {'key': k, 'permissions': api.fetch_space_permissions(k)}) \
        .group_by(_['key']) \
        .map_values(grouping_by_names) \
        .map(lambda key, violator: find_violator_by_space(key, violator, config.deny)) \
        .filter(lambda x: x.group_names or x.user_names or x.anonymous)

    return TOption(violators or None)


def find_permission_members_by_space(args: Args, config: Config) -> TDict[TOption[TList[str]]]:
    global groups_by_member

    api = ApiClient(config.base_url, os.environ['USER'], os.environ['PASSWORD'])

    groups_by_member = api.fetch_group() \
        .flat_map(lambda g: api.fetch_members(g).map(lambda m: {'member': m, 'group': g})) \
        .group_by(_['member'].username) \
        .map_values(lambda ds: ds.map(_['group'].name))

    return TDict(
        api.fetch_spaces() \
           .map(lambda s: {'key': s.key, 'name': s.name, 'permissions': api.fetch_space_permissions(s.key)}) \
           .group_by(_['name']) \
           .map_values(lambda pks: TOption(
               pks.flat_map(_["permissions"]) \
                  .flat_map(_.space_permissions) \
                  .map(lambda p: p.user_name.get()) \
                  .uniq() \
                  .filter(lambda n: groups_by_member.get(n, TList()).any(_ == args.group.get())) \
               or None)
           )
    )


def main():
    args: Args = Args.from_dict(docopt(__doc__, version=__version__))
    config: Config = Config.from_yamlf(args.config.get_or('./config.yaml'))

    if args.permission_list:
        print(find_permission_members_by_space(args, config).to_pretty_json())
    else:
        find_violators(args, config).map(lambda r: sys.exit(r.to_pretty_json()))


if __name__ == '__main__':
    main()
