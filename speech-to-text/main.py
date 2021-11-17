import os
import argparse
from tqdm.autonotebook import tqdm
from google.cloud import speech_v1p1beta1 as speech

name_folder_output = "output"
key_json = "speech-to-text-******-************.json"
name_bucket = "[bucket name]"
name_file = "[mp3 name]"

# folder check & create
if not os.path.exists(name_folder_output):
    input("\nThere is no folder. {}\nDo you want to create a folder?\nCreate when the Enter key is pressed...".format(name_folder_output))
    os.makedirs(name_folder_output, exist_ok=True)
    print("Created a folder. " + name_folder_output)
else:
    print("Checked a folder. " + name_folder_output)

# speech scan
def speech_recognize(storage_uri, credential_path):
    #client = speech.SpeechClient()
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path
    client_options = {'api_endpoint': 'us-speech.googleapis.com'}
    client = speech.SpeechClient(client_options=client_options)

    language_code = "ja-JP"     # target > Japanese
    rate_hertz = 44100          # frequency
    encoding = speech.RecognitionConfig.AudioEncoding.MP3   # target > mp3
    
    config = {
        "language_code": language_code,
        "sample_rate_hertz": rate_hertz,
        "encoding": encoding,
    }

    audio = {"uri": storage_uri}

    # less than 1 minute
    #response = client.recognize(config=config, audio=audio)

    # long data
    operation = client.long_running_recognize(config=config, audio=audio)
    print("Waiting for operation to complete...")
    response = operation.result(timeout=1800)

    return response

parser = argparse.ArgumentParser()
parser.add_argument(
    "--storage_uri",
    type=str,
    default="gs://{}/{}.mp3".format(name_bucket, name_file),    # GCS(Google Cloud Storage) URI
)
args = parser.parse_args()

response = speech_recognize(storage_uri=args.storage_uri, credential_path=key_json)

output = []
def data_set(s):
    print(s)
    output.append(s)

for i, j in enumerate(response.results):
    #alternative = result.alternatives[0]    # the most probable result
    data_set("\n\n▼▼▼▼▼▼ レスポンス {} ▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼▼\n".format(i + 1))
    for m, n in enumerate(j.alternatives):
        data_set("信頼度: {}".format(n.confidence))
        data_set(u"------ 候補 {} ------------------\n{}\n".format(m + 1, n.transcript))

# output
with open("{}/{}.txt".format(name_folder_output, name_file), 'w', encoding="utf-8") as f:
    print("Outputting...")
    for line in tqdm(output):
        f.writelines("{}\n".format(line))
