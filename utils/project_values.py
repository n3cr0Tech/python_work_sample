BIG_QUERY_DATASET_ID="drug_model"
ADVERSE_TABLE_ID="adverse_events"
ADVERSE_OUTPUT_DATA_CSV="fda_results.csv"
ADVERSE_ERROR_OUTPUT_FILENAME="error_messages.csv"
ADVERSE_ERROR_MSG_TABLE_ID = "error_messages"
ICD10_TABLE_ID="icd10"
DRUG_INFO_TABLE_ID="drug_info"
DRUG_PDFS_BUCKET_NAME="shield-aiprojects"
DRUG_PDFS_FOLDER_PATH=f"{BIG_QUERY_DATASET_ID}/data"
DRUG_PDFS_FOLDER_NAME="drug_pdfs"
DRUG_SUMMARIES_TABLE_ID = "drug_summaries"
ICD_METRICS_RETAINED_LABELS = "adverse_events_icd_metrics_retained_labels"
RETAINED_LABELS_TABLE_ID = "icd_retained_labels"
REMOVED_LABELS_TABLE_ID = "icd_removed_labels"
RANKING_TABLE_ID = "adverse_events_ranking"

JSON_CREDS_TEMPLATE="""
{
  "type": "service_account",
  "project_id": "",
  "private_key_id": "",
  "private_key": "",
  "client_email": "",
  "client_id": "",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dev-cronjob%40ai-projects-406720.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""

ADVERSE_SCHEMA = [
    {'name': 'case_number', 'type': 'STRING'},
    {'name': 'primarysourcecountry', 'type': 'STRING'},
    {'name': 'occurcountry', 'type': 'STRING'},
    {'name': 'reportercountry', 'type': 'STRING'},
    {'name': 'application_number', 'type': 'STRING'},
    {'name': 'companynumb', 'type': 'STRING'},
    {'name': 'case_date', 'type': 'INTEGER'},
    {'name': 'patientsex', 'type': 'STRING'},
    {'name': 'patientonsetage', 'type': 'STRING'},
    {'name': 'patientweight', 'type': 'STRING'},
    {'name': 'medicinalproduct', 'type': 'STRING'},
    {'name': 'drugdosagetext', 'type': 'STRING'},
    {'name': 'drugdosageform', 'type': 'STRING'},
    {'name': 'drugindication', 'type': 'STRING'},
    {'name': 'activesubstancename', 'type': 'STRING'},
    {'name': 'substance_name', 'type': 'STRING'},
    {'name': 'product_ndc', 'type': 'STRING'},
    {'name': 'manufacturer_name', 'type': 'STRING'},
    {'name': 'brand_name', 'type': 'STRING'},
    {'name': 'reactionmeddrapt', 'type': 'STRING'},
    {'name': 'reactionoutcome', 'type': 'STRING'},
    {'name': 'serious', 'type': 'STRING'},
    {'name': 'seriousnessdeath', 'type': 'STRING'},
    {'name': 'seriousnessdisabling', 'type': 'STRING'},
    {'name': 'seriousnesshospitalization', 'type': 'STRING'},
    {'name': 'seriousnesslifethreatening', 'type': 'STRING'},
    {'name': 'seriousnesscongenitalanomali', 'type': 'STRING'},    
    {'name': 'case_year', 'type': 'INTEGER'}
]

ICD10_SCHEMA = [
    {"name": "case_number", "type": "STRING"},
    {"name": "primarysourcecountry", "type": "STRING"},
    {"name": "occurcountry", "type": "STRING"},
    {"name": "reportercountry", "type": "STRING"},
    {"name": "application_number", "type": "STRING"},
    {"name": "companynumb", "type": "STRING"},
    {"name": "case_date", "type": "INTEGER"},
    {"name": "patientsex", "type": "STRING"},
    {"name": "patientonsetage", "type": "STRING"},
    {"name": "patientweight", "type": "STRING"},
    {"name": "medicinalproduct", "type": "STRING"},
    {"name": "drugdosagetext", "type": "STRING"},
    {"name": "drugdosageform", "type": "STRING"},
    {"name": "drugindication", "type": "STRING"},
    {"name": "activesubstancename", "type": "STRING"},
    {"name": "substance_name", "type": "STRING"},
    {"name": "product_ndc", "type": "STRING"},
    {"name": "manufacturer_name", "type": "STRING"},
    {"name": "brand_name", "type": "STRING"},
    {"name": "reactionmeddrapt", "type": "STRING"},
    {"name": "reactionoutcome", "type": "STRING"},
    {"name": "serious", "type": "STRING"},
    {"name": "seriousnessdeath", "type": "STRING"},
    {"name": "seriousnessdisabling", "type": "STRING"},
    {"name": "seriousnesshospitalization", "type": "STRING"},
    {"name": "seriousnesslifethreatening", "type": "STRING"},
    {"name": "seriousnesscongenitalanomali", "type": "STRING"},
    {"name": "case_year", "type": "INTEGER"},
    {"name": "icd_chapter", "type": "STRING"},
]

ICD_RETAINED_METRICS_SCHEMA = [
    {
        "mode": "NULLABLE",
        "name": "manufacturer_name",
        "type": "STRING"
    },
    {
        "mode": "NULLABLE",
        "name": "brand_name",
        "type": "STRING"
    },
    {
        "mode": "NULLABLE",
        "name": "activesubstancename",
        "type": "STRING"
    },
    {
        "mode": "NULLABLE",
        "name": "case_year",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "number_of_cases",
        "type": "FLOAT"
    },
    {
        "mode": "NULLABLE",
        "name": "number_of_patients",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "average_patient_age",
        "type": "FLOAT"
    },
    {
        "mode": "NULLABLE",
        "name": "average_patient_weight_kg",
        "type": "FLOAT"
    },
    {
        "mode": "NULLABLE",
        "name": "number_of_male_patients",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "number_of_female_patients",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "number_of_serious_outcomes",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "number_of_deaths",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "number_of_disablities",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "number_of_hospitalizations",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "number_of_lifetheartenings",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "certain_conditions_originating_in_the_perinatal_period",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "certain_infectious_and_parasitic_diseases",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "codes_for_special_purposes",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "congenital_malformations_deformations_and_chromosomal_abnormalities",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "diseases_of_the_blood_and_bloodforming_organs_and_certain_disorders_involving_the_immune_mechanism",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "diseases_of_the_circulatory_system",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "diseases_of_the_digestive_system",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "diseases_of_the_ear_and_mastoid_process",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "diseases_of_the_eye_and_adnexa",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "diseases_of_the_genitourinary_system",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "diseases_of_the_musculoskeletal_system_and_connective_tissue",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "diseases_of_the_nervous_system",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "diseases_of_the_respiratory_system",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "diseases_of_the_skin_and_subcutaneous_tissue",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "endocrine_nutritional_and_metabolic_diseases",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "external_causes_of_morbidity_and_mortality",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "eye_infection_toxoplasmal",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "factors_influencing_health_status_and_contact_with_health_services",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "injury_poisoning_and_certain_other_consequences_of_external_causes",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "mental_and_behavioural_disorders",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "neoplasms",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "not_a_diagnosis_or_procedure",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "pregnancy_childbirth_and_the_puerperium",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "procedure",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "symptoms_signs_and_abnormal_clinical_and_laboratory_findings_not_elsewhere_classified",
        "type": "INTEGER"
    },
    {
        "mode": "NULLABLE",
        "name": "median_patient_age",
        "type": "FLOAT"
    },
    {
        "mode": "NULLABLE",
        "name": "number_of_disabilities",
        "type": "INTEGER"
    }
]

LLM_AWS_PROPS ={
    "model_id": "anthropic.claude-3-5-sonnet-20240620-v1:0",
    "accept": 'application/json',
    "content_type": 'application/json',
}

LLM_CLASSIFICATION_TEMPLATE = """You're a AI Assistant with expertise in classifying and extracting informations from pdfs. 

Your job is to search for drug information in pdfs and extract certain categorial information from them. 

These Categories are:
1.) WARNINGS AND PRECAUTIONS
2.) ADVERSE REACTIONS
3.) BOXED WARNING or WARNING, this category is located around the text See full prescribing information for complete boxed warning. This is a seperate category than WARNINGS AND PRECAUTIONS

Hint:
If there is not information associated or the category is not found please return not found.  

Provide your response for the input text if a drug is found in pydantic, in a json object.
(
	"warnings_precautions": your response
	"adverse_reactions_library_of_medicine": your response
	"boxed_warning": your response
)

Human: {text} 

AI Assistant:"""

LLM_SUMMARY_TEMPLATE = """You're an AI Assistant with expertise in summarizing drug labels in 3-4 sentences. 
Some of the key information to include in the summary drug purpose, side effects active ingredients. 
Provide your response for the summary in this format below:
(
    "summary": your response
)

Do not add in any information unless found in the text.

This is the text to summarize:
{text}
"""

LLM_DRUG_SUMMARIES_SCHEMA = [
    {'name': 'brand_name', 'type': 'STRING'},
    {'name': 'summary', 'type': 'STRING'},
    {'name': 'warnings_precautions', 'type': 'STRING'},
    {'name': 'adverse_reactions_library_of_medicine', 'type': 'STRING'},
    {'name': 'boxed_warning', 'type': 'STRING'}
]