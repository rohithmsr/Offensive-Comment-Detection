import os

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

import boto3
import tensorflow as tf
from transformers import BertTokenizer

AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
LABEL_COLUMNS = ['toxic','severe_toxic','obscene','threat','insult','identity_hate']

# Input Format for prediction!
class Comment(BaseModel):
    comment_id: str
    text: str
    source: Optional[str] = None

# Download the folder output from S3
def download_s3_folder(s3, bucket_name, s3_folder, local_dir=None):
    bucket = s3.Bucket(bucket_name)
    for obj in bucket.objects.filter(Prefix=s3_folder):
        target = obj.key if local_dir is None \
            else os.path.join(local_dir, os.path.relpath(obj.key, s3_folder))
        if not os.path.exists(os.path.dirname(target)):
            os.makedirs(os.path.dirname(target))
        if obj.key[-1] == '/':
            continue
        bucket.download_file(obj.key, target)

# Prepare the model understandable input data
def prepare_data(input_text, tokenizer):
    token = tokenizer.encode_plus(
        input_text,
        max_length=256, 
        truncation=True, 
        padding='max_length', 
        add_special_tokens=True,
        return_tensors='tf'
    )
    return {
        'input_ids': tf.cast(token.input_ids, tf.float64),
        'attention_mask': tf.cast(token.attention_mask, tf.float64)
    }

## 1. Get Model Files
# Add your own s3 bucket credentials
s3 = boto3.resource(
    service_name = 's3',
    region_name='us-east-1',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

# Download the folder
# download_s3_folder(s3, 'test-rohith-1', 'bert-model-files')

# Download the file
s3.Bucket('test-rohith-1').download_file('bert-model-files/my_model_atf.h5', 'model/my_model_atf.h5')

## 2. Initialize the model and tokenizer!
model = tf.keras.models.load_model('model/my_model_atf.h5')
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello from ATF API! Aabaasam Thavirpom Friends!"}

@app.post("/predict")
async def create_item(comment: Comment):
    predictions = dict.fromkeys(LABEL_COLUMNS, 0)

    processed_data = prepare_data(comment.text, tokenizer)
    probs = model.predict(processed_data)[0]

    for i in range(len(probs)):
        predictions[LABEL_COLUMNS[i]] = 1 if probs[i] >= 0.5 else 0

    return predictions