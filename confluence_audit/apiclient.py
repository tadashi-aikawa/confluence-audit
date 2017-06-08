# -*- coding: utf-8 -*-
import requests

from owlmixin.owlcollections import TList, TDict
from typing import Type, TypeVar

from confluence_audit.models import SpacePermission, Space, Group, Member

T = TypeVar('T')


class ApiClient:
    def __init__(self, base: str, user: str, password: str):
        self.rpc_base = f'{base}/rpc/json-rpc/confluenceservice-v2'
        self.rest_base = f'{base}/rest/api'
        self.auth = (user, password)

    def __pagination_iterator(self, path: str):
        res_size = -1
        start = 0
        while res_size != 0:
            r = requests.get(
                url=f'{self.rest_base}{path}',
                params={'start': start},
                auth=self.auth,
                headers={'content-type': 'application/json'}
            ).json()
            yield r['results']
            res_size = r['size']
            start += res_size

    def __extract_results(self, cls_: Type[T], path: str) -> TList[T]:
        return cls_.from_dicts(TList(self.__pagination_iterator(path)).flatten(), restrict=False)

    def fetch_space_permissions(self, space: str) -> TList[SpacePermission]:
        res = requests.post(
            url=f'{self.rpc_base}/getSpacePermissionSets',
            data=f'["{space}"]',
            auth=self.auth,
            headers={'content-type': 'application/json'}
        )
        return SpacePermission.from_dicts(res.json())

    def fetch_spaces(self) -> TList[Space]:
        return self.__extract_results(Space, '/space')

    def fetch_group(self) -> TList[Group]:
        return self.__extract_results(Group, '/group')

    def fetch_members(self, group: Group) -> TList[Member]:
        return self.__extract_results(Member, f'/group/{group.name}/member')
