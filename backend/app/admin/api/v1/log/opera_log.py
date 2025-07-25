#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.app.admin.schema.opera_log import DeleteOperaLogParam, GetOperaLogDetail
from backend.app.admin.service.opera_log_service import opera_log_service
from backend.common.pagination import DependsPagination, PageData, paging_data
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession

router = APIRouter()


@router.get(
    '',
    summary='分页获取操作日志',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_opera_logs_paged(
    db: CurrentSession,
    username: Annotated[str | None, Query(description='用户名')] = None,
    status: Annotated[int | None, Query(description='状态')] = None,
    ip: Annotated[str | None, Query(description='IP 地址')] = None,
) -> ResponseSchemaModel[PageData[GetOperaLogDetail]]:
    log_select = await opera_log_service.get_select(username=username, status=status, ip=ip)
    page_data = await paging_data(db, log_select)
    return response_base.success(data=page_data)


@router.delete(
    '',
    summary='批量删除操作日志',
    dependencies=[
        Depends(RequestPermission('log:opera:del')),
        DependsRBAC,
    ],
)
async def delete_opera_logs(obj: DeleteOperaLogParam) -> ResponseModel:
    count = await opera_log_service.delete(obj=obj)
    if count > 0:
        return response_base.success()
    return response_base.fail()


@router.delete(
    '/all',
    summary='清空操作日志',
    dependencies=[
        Depends(RequestPermission('log:opera:clear')),
        DependsRBAC,
    ],
)
async def delete_all_opera_logs() -> ResponseModel:
    await opera_log_service.delete_all()
    return response_base.success()
