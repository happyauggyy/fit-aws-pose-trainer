import json
import time
import boto3

# Initialize AWS SDK clients
s3 = boto3.client('s3', region_name='ap-south-1')
dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')

def save_workout_to_aws(student_id, exercise_name, rep_count, form_score):
    timestamp = int(time.time())
    payload = {
        "student_id": student_id,
        "exercise": exercise_name,
        "reps": rep_count,
        "form_score": form_score,
        "timestamp": timestamp
    }
    
    # 1. Save telemetry JSON to S3 Bucket
    s3_key = f"logs/{student_id}_{timestamp}.json"
    s3.put_object(
        Bucket="vit-aws-builder-fitness-logs",
        Key=s3_key,
        Body=json.dumps(payload)
    )
    
    # 2. Record entry in AWS DynamoDB Table
    table = dynamodb.Table('WorkoutHistory')
    table.put_item(Item=payload)
    print(f"[AWS Cloud] Session logged for {student_id}")