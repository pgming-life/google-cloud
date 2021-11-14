"""pdf_tiff_scaner.py"""
import os
import json
import re
from google.cloud import vision
from google.cloud import storage

# document scan
def async_detect_document(gcs_source_uri, gcs_destination_uri, credential_path):
    mime_type = 'application/pdf'
    batch_size = 100

    #client = vision.ImageAnnotatorClient()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    client_options = {'api_endpoint': 'us-vision.googleapis.com'}
    client = vision.ImageAnnotatorClient(client_options=client_options)

    feature = vision.Feature(
        type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION)

    gcs_source = vision.GcsSource(uri=gcs_source_uri)
    input_config = vision.InputConfig(
        gcs_source=gcs_source, mime_type=mime_type)

    gcs_destination = vision.GcsDestination(uri=gcs_destination_uri)
    output_config = vision.OutputConfig(
        gcs_destination=gcs_destination, batch_size=batch_size)

    async_request = vision.AsyncAnnotateFileRequest(
        features=[feature], input_config=input_config,
        output_config=output_config)

    operation = client.async_batch_annotate_files(
        requests=[async_request])

    print('Waiting for the operation to finish.')
    operation.result(timeout=420)

# output text
def write_to_text(gcs_destination_uri, name_file_output):
    storage_client = storage.Client()
    match = re.match(r'gs://([^/]+)/(.+)', gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)
    bucket = storage_client.get_bucket(bucket_name)
    blob_list = list(bucket.list_blobs(prefix=prefix))
    print('Output files:')
    transcription = open("{}.txt".format(name_file_output), "w")

    for blob in blob_list:
        print(blob.name)
    
    for n in range(len(blob_list)):
        print("{}/{}".format(n + 1, len(blob_list)))
        output = blob_list[n]
        json_string = output.download_as_string()
        response = json.loads(json_string)

        for m in range(len(response['responses'])):
            first_page_response = response['responses'][m]
            try:
                annotation = first_page_response['fullTextAnnotation']
            except(KeyError):
                print("No annotation for this page.")

            #print('Full text:\n')
            #print(annotation['text'])
            with open("{}.txt".format(name_file_output), "a+", encoding="utf-8") as f:
                f.write(annotation['text'])
