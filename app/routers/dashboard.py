from datetime import datetime
import json
from typing import Annotated
from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request, UploadFile
from database.database import get_db
from database.database import SessionLocal
from services.auth_service import get_current_user
from schemas.user import User
from sentiment_analysis import engine
from services import dashboard_service as dashboard

router = APIRouter()

@router.get("/collections", tags=["Dashboard"])
async def get_collections_by_user(current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
  user_id = current_user.id
  collections = dashboard.get_collections_by_user(user_id=user_id, db=db)
  return collections

@router.post("/collections/create", tags=["Dashboard"])
async def create_collection(request: Request, current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
  data = await request.json()
  collection_name = data.get("collection_name")
  collection = dashboard.save_collection(collection_name=collection_name, user=current_user, db=db)
  return collection

@router.get("/collections/{collection_id}/reports", tags=["Dashboard"])
async def get_reports_by_collection(collection_id: int, current_user: User = Depends(get_current_user), db: SessionLocal = Depends(get_db)):
  collections = dashboard.get_collections_by_user(user_id=current_user.id, db=db)

  if int(collection_id) not in [collection.id for collection in collections]:
    raise HTTPException(status_code=403, detail="Unauthorized to access this collection's reports.")

  reports = dashboard.get_reports_by_collection(report_group_id=collection_id, db=db)
  return reports

@router.post("/reports/create", tags=["Dashboard"])
async def create_report(report_name: Annotated[str, Form()], 
                        collection_id: Annotated[str, Form()], 
                        file: UploadFile,
                        current_user: User=Depends(get_current_user), 
                        db: SessionLocal=Depends(get_db)):
  
  collections = dashboard.get_collections_by_user(user_id=current_user.id, db=db)
  ids = [collection.id for collection in collections]
  if int(collection_id) not in ids:
    raise HTTPException(status_code=403, detail="Unauthorized to create a report in this collection.")
    
  results, metadata, reviews, word_count, wordcloud = engine.predict(file)

  report_data = {
      "title": report_name,
      "user_id": current_user.id,
      "report_group_id": collection_id,
      "date": datetime.now(),
      **results['scores'],
      **results['number_of_reviews'],
      "word_count": json.dumps(word_count),
      "wordcloud": wordcloud,
  }
    
  report = dashboard.save_report(report_data=report_data, db=db)
  
  def save_dataset(report):
    dataset = dashboard.save_dataset(report=report, report_metadata=metadata, db=db)
    reviews_categories = dashboard.save_reviews(dataset=dataset, reviews_list=reviews, db=db)
    dashboard.save_review_categories(reviews_categories_list=reviews_categories, db=db)

  save_dataset(report)

  response = {
    "id": report.id,
    "title": report_name,
    "user_id": current_user.id,
    "collection_id": report.report_group_id,
    "date": report.date,
    "overall_score": results['scores']['overall_score'],
    "total_reviews": results['number_of_reviews']['total_reviews'],
    "fit_score": results['scores']['fit_score'],
    "fit_reviews": results['number_of_reviews']['fit_reviews'],
    "color_score": results['scores']['color_score'],
    "color_reviews": results['number_of_reviews']['color_reviews'],
    "quality_score": results['scores']['quality_score'],
    "quality_reviews": results['number_of_reviews']['quality_reviews'],
  }
  
  return response

@router.get("/reports/{report_id}", tags=["Dashboard"])
async def get_report(report_id: int, current_user: User = Depends(get_current_user), db: SessionLocal=Depends(get_db)):
  report = dashboard.get_report(report_id=report_id, db=db)

  if report.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Unauthorized to get this report.")

  report = dashboard.get_report(report_id=report_id, db=db)
  return report

@router.get("/reports/{report_id}/reviews", tags=["Dashboard"])
async def get_reviews(report_id: int,
                      page: int = Query(1, gt=0),
                      reviews_per_page: int = Query(10, gt=0, le=50),
                      current_user: User=Depends(get_current_user), 
                      db: SessionLocal = Depends(get_db)):
  report = dashboard.get_report(report_id=report_id, db=db)

  if report.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Unauthorized to get this report's reviews.")


  offset = (page - 1) * reviews_per_page
  limit = reviews_per_page
  reviews = dashboard.get_reviews(report_id=report_id, offset=offset, limit=limit, db=db)
  return reviews

@router.get("/reports/{report_id}/word_count", tags=["Dashboard"])
async def get_word_count(report_id: int, current_user: User=Depends(get_current_user), db: SessionLocal=Depends(get_db)):
  report = dashboard.get_report(report_id=report_id, db=db)

  if report.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Unauthorized to get this report's word count.")
  
  wordcloud = dashboard.get_word_count(report_id=report_id, db=db)
  return wordcloud

@router.get("/reports/{report_id}/wordcloud", tags=["Dashboard"])
async def get_wordcloud(report_id: int, current_user: User=Depends(get_current_user), db: SessionLocal=Depends(get_db)):
  report = dashboard.get_report(report_id=report_id, db=db)

  if report.user_id != current_user.id:
    raise HTTPException(status_code=403, detail="Unauthorized to get this report's wordcloud.")
  
  wordcloud = dashboard.get_wordcloud(report_id=report_id, db=db)
  return wordcloud

@router.delete("/collections/{collection_id}", tags=["Dashboard"])
def delete_collection(collection_id: int, current_user: User=Depends(get_current_user), db: SessionLocal=Depends(get_db)):
    collections = dashboard.get_collections_by_user(user_id=current_user.id, db=db)

    if int(collection_id) not in [collection.id for collection in collections]:
      raise HTTPException(status_code=403, detail="Unauthorized to access this collection's reports.")

    deleted_collection = dashboard.delete_collection(collection_id=collection_id, db=db)
    if deleted_collection is None:
        raise HTTPException(status_code=404, detail="Collection not found")
    return {"message": "Collection deleted successfully"}

@router.delete("/reports/{report_id}", tags=["Dashboard"])
def delete_report(report_id: int, current_user: User=Depends(get_current_user), db: SessionLocal=Depends(get_db)):
    report = dashboard.get_report(report_id=report_id, db=db)

    if report.user_id != current_user.id:
      raise HTTPException(status_code=403, detail="Unauthorized to delete this collection.")
    
    deleted_report = dashboard.delete_report(report_id=report_id, db=db)
    if deleted_report is None:
        raise HTTPException(status_code=404, detail="Report not found")
    return {"message": "Report deleted successfully"}
