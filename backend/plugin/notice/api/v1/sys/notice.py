#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Path

from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession
from backend.plugin.notice.schema.notice import CreateNoticeParam, DeleteNoticeParam, GetNoticeDetail, UpdateNoticeParam
from backend.plugin.notice.service.notice_service import notice_service

router = APIRouter()


@router.get('/{pk}', summary='获取通知公告详情', dependencies=[DependsJwtAuth])
async def get_notice(pk: Annotated[int, Path(description='通知公告 ID')]) -> ResponseSchemaModel[GetNoticeDetail]:
    notice = await notice_service.get(pk=pk)
    return response_base.success(data=notice)


@router.get(
    '',
    summary='分页获取所有通知公告',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_notices_paged(db: CurrentSession) -> ResponseSchemaModel[PageData[GetNoticeDetail]]:
    notice_select = await notice_service.get_select()
    page_data = await paging_data(db, notice_select)
    return response_base.success(data=page_data)


@router.post(
    '',
    summary='创建通知公告',
    dependencies=[
        Depends(RequestPermission('sys:notice:add')),
        DependsRBAC,
    ],
)
async def create_notice(obj: CreateNoticeParam) -> ResponseModel:
    await notice_service.create(obj=obj)
    return response_base.success()


@router.put(
    '/{pk}',
    summary='更新通知公告',
    dependencies=[
        Depends(RequestPermission('sys:notice:edit')),
        DependsRBAC,
    ],
)
async def update_notice(pk: Annotated[int, Path(description='通知公告 ID')], obj: UpdateNoticeParam) -> ResponseModel:
    count = await notice_service.update(pk=pk, obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '',
    summary='批量删除通知公告',
    dependencies=[
        Depends(RequestPermission('sys:notice:del')),
        DependsRBAC,
    ],
)
async def delete_notices(obj: DeleteNoticeParam) -> ResponseModel:
    count = await notice_service.delete(obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()
