"""2021/10/30"""
import os
import pdf_tiff_scaner as pt

name_folder_output = "output"
key_json = "spheric-shield-******-************.json"
name_bucket = "[bucket name]"

# single input
name_input = "[pdf name]"
name_output = "[( a-z ) and ( 0-9 ) and ( _ ) output name]"
gcs_source_uri = "gs://{0}/{1}.pdf".format(name_bucket, name_input)
gcs_destination_uri = "gs://{0}/{1}".format(name_bucket, name_output)

# multiple input
# create folder of "name_output" in advance.
names = [
    ["[pdf name 1]", "[( a-z ) and ( 0-9 ) and ( _ ) output name 1]"],
    ["[pdf name 2]", "[( a-z ) and ( 0-9 ) and ( _ ) output name 2]"],
]

# folder check & create
if not os.path.exists(name_folder_output):
    input("\nThere is no folder. {}\nDo you want to create a folder?\nCreate when the Enter key is pressed...".format(name_folder_output))
    os.makedirs(name_folder_output, exist_ok=True)
    print("Created a folder. " + name_folder_output)
else:
    print("Checked a folder. " + name_folder_output)

# single
def single_scan(gcs_source_uri, gcs_destination_uri, key_json, name_input):
    # pdf/tiff scan
    pt.async_detect_document(gcs_source_uri=gcs_source_uri, gcs_destination_uri=gcs_destination_uri + " ", credential_path=key_json)
    pt.write_to_text(gcs_destination_uri=gcs_destination_uri + " ", name_file_output=name_folder_output + "/" + name_input)

# multiple
def multiple_scan(names):
    for n in names:
        name_input = n[0]
        gcs_source_uri = "gs://{0}/{1}.pdf".format(name_bucket, name_input)
        gcs_destination_uri = "gs://{0}/{1}/{1}".format(name_bucket, n[1])
        single_scan(gcs_source_uri, gcs_destination_uri, key_json, name_input)

#single_scan(gcs_source_uri, gcs_destination_uri, key_json, name_input)
multiple_scan(names)
