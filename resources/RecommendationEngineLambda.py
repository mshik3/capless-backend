import boto3
import csv

s3 = boto3.resource("s3")
RECS_INPUTS_BUCKET = 'capless-recommendation-service-inputs'

# Retrieves S3 csv object and converts to dict {col: attribute...}
def csv_to_dict(file_name):
    csv_object = s3.Object(RECS_INPUTS_BUCKET, key=file_name)
    csv_content = csv_object.get()['Body'].read().decode('utf-8').splitlines()
    csv_dicts = []
    lines = csv.reader(csv_content)
    headers = next(lines)
    for line in lines:
        csv_dicts.append(dict(zip(headers, line)))
    return csv_dicts

# Computes quality score in an intelligent way
def calculate_quality_scores(startup_attributes_list):
    total_scores_dict = {}
    for startup_attributes in startup_attributes_list:
        company_name = startup_attributes["company_name"]
        total_scores_dict[company_name] = 0
        for key, attribute in startup_attributes.items():
            attribute = attribute.strip()
            if attribute != "None":
                total_scores_dict[company_name] += 1
    return total_scores_dict

# Helper function to compute single startup:investor match score
def compute_match_score(startup, investor, startup_ranks):
    match_score = 0.0
    for key in startup.keys():
        if key != "company_name":
            startup_preference = startup[key].strip()
            investor_attribute = investor[key].strip()
            if startup_preference == investor_attribute:
                rank = startup_ranks[key].strip()
                score = 1.0 / float(rank)
                match_score += score
    return "{:.3f}".format(match_score)

# Compute pairwise startup:investor match scores
# If attributes match, add 1/rank[attribute] to the match score
def calculate_match_scores(startup_preference_values, startup_preference_ranks, investors_attributes):
    num_attributes = len(startup_preference_ranks[0]) - 1
    match_scores_dict = {}
    for i, startup in enumerate(startup_preference_values):
        for investor in investors_attributes:
            startup_ranks = startup_preference_ranks[i]
            startup_name = startup["company_name"]
            investor_name = investor["company_name"]
            primary_key = startup_name.replace(" ", "") + ':' + investor_name.replace(" ", "")
            match_scores_dict[primary_key] = compute_match_score(startup, investor, startup_ranks)
    match_scores_dict = dict(sorted(match_scores_dict.items(), key = lambda x: x[1], reverse = True))
    return match_scores_dict

def lambda_handler(event, context):
    # Quality score calculation
    startup_attributes = csv_to_dict("startups/attributes/2021-12-28.csv")
    quality_scores = calculate_quality_scores(startup_attributes)

    # Match score calculation
    startup_preference_ranks = csv_to_dict("startups/preferences/2021-12-28_rank.csv")
    startup_preference_values = csv_to_dict("startups/preferences/2021-12-28_values.csv")
    investors_attributes = csv_to_dict("investors/attributes/2021-12-28.csv")
    match_scores = calculate_match_scores(startup_preference_values, startup_preference_ranks, investors_attributes)

    return {
        'statusCode': 200,
        'body': {
            "quality_scores": quality_scores,
            "match_scores": match_scores
        }
    }