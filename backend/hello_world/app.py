import json
import boto3
import os
import uuid
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    """
    Cette fonction génère une URL présignée.
    Elle permet au frontend d'uploader un fichier directement vers S3
    sans surcharger la Lambda.
    """
    s3_client = boto3.client("s3")

    # On récupère le nom du bucket que SAM a créé pour nous
    bucket_name = os.environ["BUCKET_NAME"]

    # On génère un identifiant unique pour le fichier
    file_id = str(uuid.uuid4())
    file_name = f"vault-{file_id}.png"  # On part sur du .png pour le test

    try:
        # On demande à S3 de créer l'autorisation d'upload (méthode PUT)
        # L'URL sera valide pendant 3600 secondes (1 heure)
        presigned_url = s3_client.generate_presigned_url(
            "put_object",
            Params={
                "Bucket": bucket_name,
                "Key": file_name,
                "ContentType": "image/png",
            },
            ExpiresIn=3600,
        )
    except ClientError as e:
        print(f"Erreur S3: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"message": "Impossible de générer l'URL"}),
        }

    # On renvoie l'URL au frontend
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Origin": "*",  # Autorise ton futur site web à appeler cette API
            "Access-Control-Allow-Methods": "GET,OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
        },
        "body": json.dumps({"uploadUrl": presigned_url, "fileName": file_name}),
    }
