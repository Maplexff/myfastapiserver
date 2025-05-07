from sqlalchemy.orm import Session
from . import models, schemas
from sqlalchemy import delete   
    
def get_user_by_name(db: Session, name: str):
    return db.query(models.User).filter(models.User.name == name).first()

def get_user_by_id(db: Session, id: int):
    return db.query(models.User).filter(models.User.id == id).first()    
    
def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()
    
    
def create_user(db: Session, user: schemas.UserCreate):
    # fake_hashed_password = user.password + "notreallyhashed"
    fake_hashed_password = user.password
    db_user = models.User(name=user.name, password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def edit_username_id(db: Session, user: schemas.User):
    db.query(models.User).filter_by(id=user.id).update({"name": user.name})
    db.commit()

def edit_pwd_id(db: Session, user: schemas.UserInfo):
    db.query(models.User).filter_by(id=user.id).update({"password":user.password})
    db.commit()

    # # fake_hashed_password = user.password + "notreallyhashed"
    # db_user = models.User(name=user.name, password=fake_hashed_password)
    # db.add(db_user)
    # db.commit()
    # db.refresh(db_user)
    # return db_user

def create_historyitem(db: Session, history: schemas.HistoryItemCreate):
    

    # db_item = models.History(image=history.image,
    #                          time=history.time,
    #                          location=history.location,
    #                          latlng=history.latlng,
    #                          reportid=history.reportid,
    #                          predlabel=history.predlabel,
    #                          predclass=history.predclass,
    #                          predscore=history.predscore )

    db.add(history)
    db.commit()
    db.refresh(history)
    return history

def clear_all_data(db: Session,tablename:str):
    try:
        if(tablename == "history"):
            # 清空 History 表中的所有数据
            db.execute(delete(models.History))
            db.commit()
            return {"message": "History表中的所有数据已清空"}
        elif(tablename == "user"):
            # 清空 User 表中的所有数据
            db.execute(delete(models.User))
            db.commit()
            return {"message": "User表中的所有数据已清空"}
        elif(tablename == "all"):
            # 清空 History 表中的所有数据
            db.execute(delete(models.History))
            # 清空 User 表中的所有数据
            db.execute(delete(models.User))
            db.commit()
            return {"message": "两张表中的所有数据已清空"}
    
    except Exception as e:
        db.rollback()  # 如果出现错误，回滚事务
        return {"error": str(e)}