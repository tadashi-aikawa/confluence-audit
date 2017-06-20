# -*- coding: utf-8 -*-
from owlmixin import OwlMixin, TOption, TList, OwlEnum


class Status(OwlEnum):
    SET_PAGE_PERMISSIONS = 'SETPAGEPERMISSIONS'
    REMOVE_PAGE = 'REMOVEPAGE'
    EDIT_BLOG = 'EDITBLOG'
    REMOVE_OWN_CONTENT = 'REMOVEOWNCONTENT'
    EDIT_SPACE = 'EDITSPACE'
    SET_SPACE_PERMISSIONS = 'SETSPACEPERMISSIONS'
    REMOVE_MAIL = 'REMOVEMAIL'
    VIEW_SPACE = 'VIEWSPACE'
    REMOVE_BLOG = 'REMOVEBLOG'
    EXPORT_PAGE = 'EXPORTPAGE'
    COMMENT = 'COMMENT'
    CREATE_ATTACHMENT = 'CREATEATTACHMENT'
    REMOVE_ATTACHMENT = 'REMOVEATTACHMENT'
    REMOVE_COMMENT = 'REMOVECOMMENT'
    EXPORT_SPACE = 'EXPORTSPACE'


class Violator(OwlMixin):
    space: TOption[str]
    user_names: TList[str]
    group_names: TList[str]
    anonymous: bool


class SpacePermissionItem(OwlMixin):
    type: Status
    user_name: TOption[str]
    group_name: TOption[str]


class SpacePermission(OwlMixin):
    type: Status
    space_permissions: TList[SpacePermissionItem]


class Space(OwlMixin):
    key: str
    name: str


class Group(OwlMixin):
    name: str


class Member(OwlMixin):
    username: str
    display_name: str


class Deny(OwlMixin):
    anonymous: TOption[bool]
    group_names: TOption[TList[str]]
    join_group_names: TOption[TList[str]]
    excepts: TOption[TList[str]]


class Config(OwlMixin):
    base_url: str
    deny: TList[Deny]


class Args(OwlMixin):
    config: TOption[str]
