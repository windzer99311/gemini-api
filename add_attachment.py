import uuid
def return_attachment(session,file_data):
    session.verify = False
    filename="reference.png"
    upload_api = "https://push.clients6.google.com/upload/"
    upload_headers = {
        "x-goog-upload-protocol": "resumable",
        "content-type": "application/x-www-form-urlencoded;charset=UTF-8",
        "push-id": "feeds/mcudyrk2a4khkz",
        "x-goog-upload-command": "start",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
        "priority": "u=1, i"
    }
    upload_response = session.post(upload_api, headers=upload_headers)
    upload_id = upload_response.headers.get("X-GUploader-UploadID")
    print(f"Extracted Upload ID: {upload_id}")

    upload_blob_api = "https://push.clients6.google.com/upload/"

    params = {
        "upload_id": upload_id,
        "upload_protocol": "resumable"
    }

    blob_headers = {
        "content-type": "application/x-www-form-urlencoded;charset=utf-8",
        "push-id": "feeds/mcudyrk2a4khkz",
        "x-goog-upload-command": "upload, finalize",
        "x-goog-upload-offset": "0",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/151.0.0.0 Safari/537.36",
        "priority": "u=1, i"
    }
    blob_response = session.post(
        upload_blob_api,
        params=params,
        headers=blob_headers,
        data=file_data
    )
    uploaded_blob_url=blob_response.text
    attachment_data = [
        [
            [
                uploaded_blob_url,
                1,
                None,
                "image/jpeg",
                str(uuid.uuid4())
            ],
            filename,
            None, None, None, None, None, None,
            [0]
        ]
    ]
    return attachment_data
