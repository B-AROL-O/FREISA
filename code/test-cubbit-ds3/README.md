# test-cubbit-ds3

## Introduction

The [Cubbit Cloud](https://web.cubbit.io/) service, that offers TBs of space, by now does not offer an API compatible with Amazon S3 Cloud Storage.

Otherwise there's the possibility to use [Cubbit DS3 Object Storage](https://console.cubbit.eu/signin) that supports most of AWS S3 APIs.

## Register and Create Bucket

* Create an account in <https://console.cubbit.eu/signup>
* Create a new bucket by pressing "+ Create bucket"
* Generate the Keys of the repository by clicking "API keys" and then "+ Generate new client API key". Save the *Access key ID* and the *Secret access key*

## Sample code

Under *code/test-cubbit-ds3* can be found a file named *code.ipynb* that represents a sample code for the basic actions that can be performed using python functions.

### Prerequisites

* Python Version >= 3.8
* "boto3" Python library
* Internet connection

### Functions

The sample script is divided into two parts:

* The creation of the session: Once the endpoint (to <https://s3.cubbit.eu>) is stated, it is possible to use the Access key and the Secret key to create a Cubbit's S3 service and then instantiate an S3 client.
* The Read/Write functions: With an active session, the client can use the R/W to access the database. In particular these allow:
  * Listing of all the bucket present in repository
  * Listing of all the objects present in a bucket
  * Uploading a file into a bucket
  * Downloading an object from a bucket
  * Deleting an object from a bucket
  * Deleting a bucket
  
## Resources

* <https://docs.cubbit.io/guides/s3-api>
* <https://docs.cubbit.io/guides/access-control-list>

<!-- EOF -->
