## Running a Step
    - use command like so:
        python -m Step_N.src.driver


## .env variables
    - Create a .env file at the root dir of this project
    - PROJECT_ID = "get this from Google Cloud console website"
    - CRONJOB_ID = "whatever unique identifier you want for your cronjob"
    - BUCKET_NAME = "bucket name that will be used to store and retrieve files (e.g. shield-aiprojects)"
    - PRIVATE_KEY_ID = "get this GCP API key from Google console website"
    - CLIENT_EMAIL = "email to be used by cronjob"
    - CLIENT_ID = "id assigned to GCP role being used by cronjob"
    - GCP_SECRETS_PROJECT_NUMBER = "From the GCP secrets manager, the project number used for AWS secret"
    - GCP_AWS_SECRET_ID = "from GCP secrets manager (e.g. AWS_SECRETS_API_KEY)"


## Running Unit Test
- Example of running unit tests for Step 10
    - pytest Step_10\tests\unit_tests -vv
    - the '-vv' part gives a more verbose output (e.g. showing list of pass/fail and test run percent complete)
