import json
import boto3


s3 = boto3.resource("s3")
RAW_QUALITY_SCORES_BUCKET = "capless-raw-quality-scores"
RAW_MATCH_SCORES_BUCKET = "capless-raw-match-scores"


def get_latest_json_content(bucket_name, path):
    # Fetch filename from latest
    latest = path + "latest"
    content_object = s3.Object(bucket_name, key=latest)
    file_name = path + content_object.get()["Body"].read().decode("utf-8")

    # Fetch latest file content
    content_object = s3.Object(bucket_name, key=file_name)
    file_content = content_object.get()["Body"].read().decode("utf-8")
    return json.loads(file_content)


def generate_match_results(quality_scores):
    match_results = {}

    for quality_item in quality_scores:
        result_item = {}
        company_name = quality_item["primary_key"]

        match_score_path = company_name + "/"
        match_scores = get_latest_json_content(
            RAW_MATCH_SCORES_BUCKET, match_score_path
        )

        quality_score = quality_item["quality_score"]

        for match_item in match_scores:
            if not result_item.get(company_name):
                result_item[company_name] = []

            match_result_item = {}

            match_result_item["name"] = match_item["matched_company"]
            match_result_item["series"] = match_item["matched_company_info"]["series"]
            match_result_item["industry"] = match_item["matched_company_info"][
                "industry"
            ]
            match_result_item["capTable"] = match_item["matched_company_info"][
                "capTable"
            ]
            match_result_item["interested"] = match_item["matched_company_info"][
                "interested"
            ]
            match_result_item["total_score"] = str(
                float(quality_score) + float(match_item["match_score"])
            )

            result_item[company_name].append(match_result_item)

        sorted_result_list = sorted(
            result_item[company_name],
            key=lambda item: item["total_score"],
            reverse=True,
        )
        result_item[company_name] = sorted_result_list

        match_results.update(result_item)

    return match_results


def lambda_handler(event, context):

    quality_scores = get_latest_json_content(RAW_QUALITY_SCORES_BUCKET, "")

    generated_match_results = generate_match_results(quality_scores)

    ### write to S3 folder with these results

    for resulting_company in generated_match_results.keys():
        file_name = resulting_company + ".json"

        file_contents = json.dumps(generated_match_results[resulting_company])

        write_object = s3.Object("capless-startup-data", file_name)
        write_object.put(Body=file_contents)

    return {"statusCode": 200, "body": generated_match_results}
