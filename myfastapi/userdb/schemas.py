from typing import List, Optional
from pydantic import BaseModel
from fastapi import UploadFile, File
import base64
# class Items(BaseModel):
#     title: str
#     description: Optional[str] = None
    
    
# class Item(Items):
#     id: int
#     owner_id: int
#     class Config:
#         orm_mode = True
    
    
class Users(BaseModel):
    name: str
    
    
class UserCreate(Users):
    password: str
    
    
class User(Users):
    id: int
    # items: List[Item] = []
    
    # 向 Pydantic 提供配置
    class Config:
        orm_mode = True
        from_attributes=True

class UserInfo(Users):
    password: str
    # items: List[Item] = []
    
    # 向 Pydantic 提供配置
    class Config:
        orm_mode = True    
        from_attributes=True   

class UserCheck(User):
    checkinfo: bool  # 仅扩展字段，无需重复定义Config

class UserPwd(BaseModel):
    id: int
    password: str
        # 向 Pydantic 提供配置
    class Config:
        orm_mode = True   
        from_attributes=True

class HistoryItemCreate(BaseModel):
    image: str
    time: str
    location: str
    lat: str
    lng: str
    reportid: str
    predlabel: str
    predclass: str
    predscore: str
    class Config:
        orm_mode = True  
        from_attributes=True 

class HistoryItem(HistoryItemCreate):
    imageid: str
    class Config:
        orm_mode = True   
        from_attributes=True


class HistoryItemResponse(BaseModel):
    imageid: int
    image_base64: str  # BLOB转Base64
    time: str
    location: str
    lat: str
    lng: str
    reportid: int
    predlabel: str
    predclass: str
    predscore: str
    class Config:
        orm_mode = True  
        from_attributes=True
    
    @classmethod
    def from_sqlalchemy_model(cls, item):
        # 如果图片字段不为空，进行Base64编码
        image_base64 = None
        if item.image:
            image_base64 = base64.b64encode(item.image).decode('utf-8')
        # 生成Pydantic模型
        return cls(
            imageid=item.imageid,
            image_base64=image_base64,
            time=item.time,
            location=item.location,
            lat=str(item.lat) if item.lat is not None else None,
            lng=str(item.lng) if item.lng is not None else None,
            reportid=item.reportid,
            predlabel=item.predlabel,
            predclass=item.predclass,
            predscore=item.predscore
        )

class PaginationMeta(BaseModel):
    current_page: int
    current_record: int
    page_size: int
    total_records: int
    total_pages: int
    has_next_page: bool
    class Config:
        orm_mode = True 
        from_attributes=True


class PaginatedResponse(BaseModel):
    data: list[HistoryItemResponse]
    pagination: PaginationMeta


# @classmethod
# def from_sqlalchemy_model(cls, item):
#     # 如果图片字段不为空，进行Base64编码
#     image_base64 = None
#     if item.image:
#         image_base64 = base64.b64encode(item.image).decode('utf-8')
#     # 生成Pydantic模型
#     return cls(
#         id=item.id,
#         image_base64=image_base64,
#         time=item.time,
#         location=item.location,
#         lat=item.lat,
#         lng=item.lng,
#         report_id=item.report_id,
#         pred_label=item.pred_label,
#         pred_score=item.pred_score
#     )


