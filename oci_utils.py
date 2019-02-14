import glob
import os
import utils
import oci
from oci.object_storage.models import CreateBucketDetails


def upload_to_object_storage(config, directory, bucket_name, filename_list):
    compartment_id = config["compartment"]
    object_storage = oci.object_storage.ObjectStorageClient(config)
    namespace = object_storage.get_namespace().data

    try:
        object_storage.get_bucket(namespace, bucket_name)
        print("Bucket already exists: {!r}".format(bucket_name))
    except:
        print("Creating bucket: {!r} in compartment: {!r}".format(bucket_name, compartment_id))
        request = CreateBucketDetails()
        request.compartment_id = compartment_id
        request.name = bucket_name
        object_storage.create_bucket(namespace, request)
    
    for filename in filename_list:
        with open(os.path.join(directory, filename), 'rb') as f:
            print("Uploading file: {!r}".format(filename))
            object_storage.put_object(namespace, bucket_name, filename, f)


def download_from_object_storage(config, directory, bucket_name, object_name_list):
    object_storage = oci.object_storage.ObjectStorageClient(config)
    namespace = object_storage.get_namespace().data

    # verify local folders to create
    object_folder_list = set(o.rsplit("/", 1)[0] for o in object_name_list)
    for object_folder in object_folder_list:
        utils.create_directory(os.path.join(directory, object_folder))
    
    for object_name in object_name_list:
        print('Downloading object: {}'.format(object_name))
        get_obj = object_storage.get_object(namespace, bucket_name, object_name)
        with open(os.path.join(directory, object_name), 'wb') as f:
            for chunk in get_obj.data.raw.stream(1024 * 1024, decode_content=False):
                f.write(chunk)


def syncronize_with_object_storage(config, directory, bucket_name):
    object_storage = oci.object_storage.ObjectStorageClient(config)
    namespace = object_storage.get_namespace().data

    # verify cloud and local objects to syncronize
    object_list = object_storage.list_objects(namespace, bucket_name)
    cloud_object_name_list = [o.name for o in object_list.data.objects]
    local_object_name_list = glob.glob(directory + "**/*.*", recursive=True)
    local_object_name_list = list(map(lambda o: o.replace("\\", "/").replace(directory, ""), local_object_name_list))
    objects_to_download = set(cloud_object_name_list) - set(local_object_name_list)
    objects_to_upload = set(local_object_name_list) - set(cloud_object_name_list)

    # download cloud objects
    download_from_object_storage(config, directory, bucket_name, objects_to_download)

    # upload local objects
    upload_to_object_storage(config, directory, bucket_name, objects_to_upload)