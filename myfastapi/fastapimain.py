from typing import Union,Annotated,List

from fastapi import FastAPI,File, UploadFile, HTTPException,Depends,Query,Form
from fastapi.responses import JSONResponse, StreamingResponse
from contextlib import asynccontextmanager
from PIL import Image
import io
from pathlib import Path

from tools.single_test import *

from sqlmodel import Session, SQLModel, create_engine, select

from sqlalchemy.orm import Session
from sqlalchemy import func
from userdb import crud, schemas
from userdb.database import get_db
from userdb import models
from math import ceil
import uvicorn

########       Img Torch

CACHE_DIR = Path("./img_cache")
CACHE_DIR.mkdir(parents=True, exist_ok=True)

@asynccontextmanager
async def lifespan(app: FastAPI):
    server_load_model()
    # # Load the ML model
    # ml_models["answer_to_everything"] = fake_answer_to_everything_ml_model
    yield
    # # Clean up the ML models and release the resources
    # ml_models.clear()
    # server.should_exit = True



########       Img Torch

app = FastAPI(lifespan=lifespan)




########       Database

@app.post("/users/register", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_name(db, name=user.name)
    if db_user:
        # raise HTTPException(status_code=400, detail="Name already registered")
        return schemas.User(
                id = -1,
                name = user.name
        )
    return crud.create_user(db=db, user=user)
    
    
@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users

@app.post("/users/editnamebyid", response_model=schemas.UserCheck)
def editusernamebyid(user: schemas.User, db: Session = Depends(get_db)):
    samename = crud.get_user_by_name(db, name=user.name)
    if samename:
            return schemas.UserCheck(
                id=samename.id,
                name=samename.name,
                checkinfo=False
        )
    crud.edit_username_id(db, user)
    edit_user = crud.get_user_by_id(db, id=user.id)
    if edit_user and user.name == edit_user.name:
        return schemas.UserCheck(
                   id=edit_user.id,
                   name=edit_user.name,
                   checkinfo=True
        )
    else:
        return schemas.UserCheck(
            id=edit_user.id, 
            name=user.name,
            checkinfo=False
        )

@app.post("/users/editpwdbyid", response_model=schemas.UserCheck)
def editpwdbyid(user: schemas.UserPwd, db: Session = Depends(get_db)):
    crud.edit_pwd_id(db, user)
    edit_user = crud.get_user_by_id(db, id=user.id)
    if edit_user and user.password == edit_user.password:
        return schemas.UserCheck(
                   id=edit_user.id,
                   name=edit_user.name,
                   checkinfo=True
        )
    else:
        return schemas.UserCheck(
            id=edit_user.id,
            name=user.name,
            checkinfo=False
        )

@app.post("/users/logininfo", response_model=schemas.UserInfo)
def login_users(user: schemas.UserCreate, db: Session = Depends(get_db)):
    login_user = crud.get_user_by_name(db, name=user.name)
    return login_user

@app.post("/users/login", response_model=schemas.UserCheck)
def login_users(user: schemas.UserCreate, db: Session = Depends(get_db)):
    login_user = crud.get_user_by_name(db, name=user.name)
    # if(user.name == login_user.name and user.password == login_user.password):
    #        # 实例化UserCheck对象并返回
    if login_user and user.password == login_user.password:
        return schemas.UserCheck(
                   id=login_user.id,
                   name=login_user.name,
                checkinfo=True
        )
    else:
        return schemas.UserCheck(
            id=-1,  # 表示无效用户
            name=user.name,
            checkinfo=False
        )



########       Database


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/ping")
async def connectivity_test():
    return JSONResponse(content={"status": "success", "message": "Server is reachable"})

# @app.post("/predict")
# async def predict(file: UploadFile = File(...)):
#     if not file.content_type.startswith("image/"):
#         raise HTTPException(status_code=400, detail="File must be an image")

#     # contents = await file.read()
#     # with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
#     #     tmp.write(contents)
#     #     tmp_path = tmp.name

#     contents = await file.read()
#     filename = CACHE_DIR / f"uploaded_{file.filename}"
#     with open(filename, "wb") as f:
#         f.write(contents)

#     result = server_image(str(filename))
#     # os.remove(str(filename))  # Cleanup temp file
#     return JSONResponse(content={"pred_class": result['pred_class'], "pred_label": result['pred_label'],"pred_score":result['pred_score']})


@app.post("/predict")
async def predict(
                  time: str= Form(...),
                  location: str= Form(...),
                  lat: str= Form(...),
                  lng: str= Form(...),
                  reportid: str= Form(...),
                  file: UploadFile = File(...),
                  db: Session = Depends(get_db)
                  ):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # contents = await file.read()
    # with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
    #     tmp.write(contents)
    #     tmp_path = tmp.name


    # 检查reportid是否在User表中存在
    user = db.query(models.User).filter(models.User.id == reportid).first()
    if not user:
        raise HTTPException(status_code=404, detail="User with the given reportid not found")

    contents = await file.read()
    filename = CACHE_DIR / f"uploaded_{file.filename}"
    with open(filename, "wb") as f:
        f.write(contents)

    result = server_image(str(filename))
    os.remove(str(filename))  # Cleanup temp file
    
    # 创建History实例并填充字段
    new_history_item = models.History(
        image=contents,  # 将文件内容作为BLOB存储
        time=time,
        location=location,
        lat=lat,
        lng=lng,
        reportid=reportid,  # 假设reportid传入的是字符串类型，会被转换为整数
        predlabel=result['pred_label'],
        predclass=result['pred_class'],
        predscore=result['pred_score']
    )
    crud.create_historyitem(db=db,history=new_history_item)
    # os.remove(str(filename))  # Cleanup temp file
    return JSONResponse(content={"pred_class": result['pred_class'], "pred_label": result['pred_label'],"pred_score":result['pred_score']})



# 批量转换函数
def batch_convert_to_history_item_response(db_session: Session, records) -> List[schemas.HistoryItemResponse]:
    return [schemas.HistoryItemResponse.from_sqlalchemy_model(record) for record in records]


@app.get("/records/", response_model=schemas.PaginatedResponse)
async def get_records(
    page: int = Query(1, ge=1),
    # page: int = Form(...),
    page_size: int = Query(10, le=100),
    db: Session = Depends(get_db)
):

    # 计算总数和总页数
    total_records = db.query(func.count(models.History.imageid)).scalar()
    total_pages = ceil(total_records / page_size) if total_records else 0
    if total_records > 0:
        if page <= total_pages:
            if page == total_pages:
               current_record = total_records - (page - 1) * page_size
            else:
               current_record = page_size
        else:
            current_record = page_size
    else:
        current_record =  0
    



    # 获取分页数据
    records = db.query(models.History)\
        .order_by(models.History.imageid)\
        .offset((page - 1) * page_size)\
        .limit(page_size)\
        .all()
    
    # # 将 BLOB 数据转换为 base64 编码字符串
    # for record in records:
    #     schemas.HistoryItemResponse.from_obj(record)
    #     # record['image_base64'] = blob_to_base64(record['image'])
    #     # del record['image']  # 删除原来的 BLOB 字段

    # 构建响应
    return {
        "data": batch_convert_to_history_item_response(db, records),
        "pagination": {
            "current_page": page,
            "current_record": current_record,
            "page_size": page_size,
            "total_records": total_records,
            "total_pages": total_pages,
            "has_next_page": page < total_pages
        }
    }


@app.get("/image/{imageid}")
async def get_image(imageid: str, db: Session = Depends(get_db)):
    record = db.query(schemas.HistoryItemResponse).filter(schemas.HistoryItemResponse.imageid == imageid).first()
    return StreamingResponse(
        io.BytesIO(record.image), 
        media_type="image/jpeg",
        headers={"Content-Length": str(len(record.image))}
    )


@app.delete("/cleartable/{tablename}")
def clear_all_data_endpoint(tablename: str,db: Session = Depends(get_db)):
    return crud.clear_all_data(db,tablename)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="192.168.31.178", port=8000)