import boto3
import csv
import datetime
import time
import json

s3 = boto3.resource("s3")
RECS_INPUTS_BUCKET = "capless-recommendation-service-inputs"

# Retrieves S3 csv object and converts to dict {col: attribute...}
def csv_to_dict(file_name):
    csv_object = s3.Object(RECS_INPUTS_BUCKET, key=file_name)
    csv_content = csv_object.get()["Body"].read().decode("utf-8").splitlines()
    csv_dicts = []
    lines = csv.reader(csv_content)
    headers = next(lines)
    for line in lines:
        csv_dicts.append(dict(zip(headers, line)))
    return csv_dicts


# Computes quality score in an intelligent way
def calculate_quality_scores(startup_attributes_list):
    total_scores_list = []
    for startup_attributes in startup_attributes_list:
        total_scores_dict = {}
        company_name = startup_attributes["company_name"]
        total_scores_dict["company_name"] = company_name
        total_scores_dict["primary_key"] = company_name.replace(" ", "_")
        total_scores_dict["quality_score"] = 0
        num_attributes = len(startup_attributes)
        for key, attribute in startup_attributes.items():
            attribute = attribute.strip()
            if attribute != "None":
                total_scores_dict["quality_score"] += 1
        total_scores_dict["quality_score"] /= num_attributes
        total_scores_list.append(total_scores_dict)
    return total_scores_list


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
def calculate_match_scores(
    startup_preference_values, startup_preference_ranks, investors_attributes
):
    num_attributes = len(startup_preference_ranks[0]) - 1
    matches = {}
    for i, startup in enumerate(startup_preference_values):
        match_scores_list = []
        for investor in investors_attributes:
            match_scores_dict = {}
            startup_ranks = startup_preference_ranks[i]
            startup_name = startup["company_name"]
            investor_name = investor["company_name"]
            match_scores_dict["primary_key"] = (
                startup_name.replace(" ", "") + ":" + investor_name.replace(" ", "")
            )
            match_scores_dict["match_score"] = compute_match_score(
                startup, investor, startup_ranks
            )
            match_scores_dict["company_name"] = startup_name
            match_scores_dict["matched_company"] = investor_name
            match_scores_dict["matched_company_info"] = {
                "series": investor["fundraising_round"].strip(),
                "industry": investor["industry"].strip(),
                "capTable": investor["revenue"].strip(),
                "interested": True,
            }
            match_scores_list.append(match_scores_dict)
        match_scores_list = sorted(
            match_scores_list, key=lambda x: x["match_score"], reverse=True
        )

        company_id = startup["company_name"].replace(" ", "_")
        matches[company_id] = match_scores_list

    return matches


def format_and_upload_to_s3(quality_scores, matches):
    date_file_name = (
        datetime.datetime.today().strftime("%Y-%m-%d")
        + "-"
        + str(int(time.time()))
        + ".json"
    )

    # Upload quality score data
    file_contents = json.dumps(quality_scores)
    write_object = s3.Object("capless-raw-quality-scores", date_file_name)
    write_object.put(Body=file_contents)

    # Update latest
    write_object = s3.Object("capless-raw-quality-scores", "latest")
    write_object.put(Body=date_file_name)

    # Upload match score data
    for company_name, match_data in matches.items():
        file_contents = json.dumps(match_data)
        write_object = s3.Object(
            "capless-raw-match-scores", company_name + "/" + date_file_name
        )
        write_object.put(Body=file_contents)

        # Update latest
        write_object = s3.Object("capless-raw-match-scores", company_name + "/latest")
        write_object.put(Body=date_file_name)


def lambda_handler(event, context):
    # Quality score calculation
    startup_attributes = csv_to_dict("startups/attributes/2021-12-28.csv")
    quality_scores = calculate_quality_scores(startup_attributes)

    # Match score calculation
    startup_preference_ranks = csv_to_dict("startups/preferences/2021-12-28_rank.csv")
    startup_preference_values = csv_to_dict(
        "startups/preferences/2021-12-28_values.csv"
    )
    investors_attributes = csv_to_dict("investors/attributes/2021-12-28.csv")
    matches = calculate_match_scores(
        startup_preference_values, startup_preference_ranks, investors_attributes
    )

    format_and_upload_to_s3(quality_scores, matches)

    return {
        "statusCode": 200,
        "body": {"quality_scores": quality_scores, "match_scores": matches},
    }
