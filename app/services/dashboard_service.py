from base64 import b64encode
from datetime import datetime
import json
from schemas.user import User
from schemas.report_group import ReportGroup
from schemas.review import Review
from schemas.dataset import Dataset
from database.database import SessionLocal
from schemas.report import Report
from schemas.review_categories import review_categories
from sqlalchemy.orm import joinedload, defer

def save_collection(collection_name: str, user: User, db: SessionLocal):
  report_group = ReportGroup.ReportGroupCreate(name=collection_name, user_id=user.id)
  db_report_group = ReportGroup(**report_group.dict())
  db.add(db_report_group)
  db.commit()
  db.refresh(db_report_group)
  return db_report_group

def save_report(report_data: dict, db: SessionLocal):
  report = Report.ReportCreate(**report_data)
  db_report = Report(**report.dict())
  db.add(db_report)
  db.commit()
  db.refresh(db_report)
  return db_report

def save_dataset(report: Report, report_metadata: dict, db: SessionLocal):
  dataset_create_data = Dataset.DatasetCreate(title=report_metadata['dataset_title'], report_id=report.id, date=datetime.now())
  db_dataset = Dataset(**dataset_create_data.dict())
  db.add(db_dataset)
  db.commit()
  db.refresh(db_dataset)
  return db_dataset

def save_reviews(dataset: Dataset, reviews_list: list, db: SessionLocal):
  reviews_categories = []
  for review in reviews_list:
    review_create_data = Review.ReviewCreate(dataset_id=dataset.id, 
                                              review_number=review['reviewNumber'],
                                              review_text=review['reviewText'],
                                              prediction=review['overall'],
                                              fit_score=review['fit'],
                                              color_score=review['color'],
                                              quality_score=review['quality'])
    db_review = Review(**review_create_data.dict())
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    reviews_categories.append({"review_id": db_review.id, "category": review['category']})
  return reviews_categories

def save_review_categories(reviews_categories_list: list, db: SessionLocal):
  for review_category in reviews_categories_list:
    for category in review_category['category']:
      db.execute(review_categories.insert().values(review_id=review_category['review_id'], category_id=category))
      db.commit()

def get_collection(collection_id: int, db: SessionLocal):
  collection = db.query(ReportGroup).filter_by(id=collection_id).first()
  return collection

def get_collections_by_user(user_id: int, db: SessionLocal):
  collections = db.query(ReportGroup).filter_by(user_id=user_id).all()
  return collections

def get_reports_by_collection(report_group_id: int, db: SessionLocal):
  reports = reports = db.query(Report).options(defer(Report.wordcloud)).filter_by(report_group_id=report_group_id).all()
  return reports

def get_report(report_id: int, db: SessionLocal):
  report = db.query(Report).options(defer(Report.wordcloud), defer(Report.word_count)).filter_by(id=report_id).first()
  return report

def get_reports_info_by_user(user_id: int, db: SessionLocal):
  reports = db.query(Report).filter_by(user_id=user_id).all()
  reports_ids = {report.id: report.title for report in reports}
  return reports_ids

def get_reviews(report_id: int, offset: int, limit: int, db: SessionLocal):
  reviews = (
    db.query(Review)
    .options(joinedload(Review.categories))
    .join(Dataset)
    .filter(Dataset.report_id == report_id)
    .order_by(Review.review_number.asc())
    .offset(offset)
    .limit(limit)
    .all()
  )
  return reviews

def get_word_count(report_id: int, db: SessionLocal):
  report = db.query(Report).filter_by(id=report_id).first()
  if report is None:
    return {'error': f'Report with id={report_id} not found'}
  word_count = json.loads(report.word_count)
  return {'word_count': word_count}

def get_wordcloud(report_id: int, db: SessionLocal):
  report = db.query(Report).filter_by(id=report_id).first()
  if report is None:
    return {'error': f'Report with id={report_id} not found'}
  wordcloud_b64 = b64encode(report.wordcloud).decode('utf-8')
  return {'wordcloud': wordcloud_b64}
  
def delete_collection(collection_id: int, db: SessionLocal):
  collection = db.query(ReportGroup).filter(ReportGroup.id == collection_id).first()
  if not collection:
    return None
  db.delete(collection)
  db.commit()
  return collection

def delete_report(report_id: int, db: SessionLocal):
  report = db.query(Report).filter(Report.id == report_id).first()
  if not report:
    return None
  db.delete(report)
  db.commit()
  return report