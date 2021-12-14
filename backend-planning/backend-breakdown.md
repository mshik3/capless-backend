## Background

This is a deep dive into every portion of the backend infrastructure, including diagrams, estimates, and required components for MVP.

> All estimates are in dev hours

## Overall Infrastructure Diagram

![Diagram](Diagram.png)

## Breakdown of each service

### Core Service

### Recommendations Service
* Need vectors for all VCs / Startups
  * Attributes, how well they've filled out profile, how much they're paying us, profile age, number of times logged in, quality score
* Match Score: For every VC, scan through every startup. Mount data from DDB into a CSV file in S3 maybe. Compare ranked preference list to list of attributes and compute score. Store symmetric score in (startup, VC) table.
  * Job to mount DDB into S3 which main algo depends on, keeps cheaper snapshot history in S3
* Sentement Score: Multiplier we use based on if there has been a like or not. Example: 
  * Like: 2
  * Not like: 1/2
  * No action: 1
* Time Score: Multiplier we use that changes everyday after an action is taken:
  * Days since company profile has been viewed
  * Days since dislike
* View Score: Number that ranks the feed, aggregate via linear combination
  * Quality
  * Match
  * Sentiment
* Input data
  * S3 Buckets: VC, Startup
  * Single file to capture snapshot for whole day of all attributes and preferences of every company
* Scoring Job (Daily Lambda)
  * Quality job -> quality score file in S3
    * dict{companyA}:score
    * Extra metadata if we want like per attribute score
  * Match job -> match score file in S3
    * dict{companyA,companyB}:score
* Combining Job
  * Combine job (view score) -> linear combination of full scores
  * Parses S3 quality and match score into pandas table
  * Formula: view_score(companyA,companyB): (Time * Sentement)(Quality + Match)
  * Store all view_scores in JSON:
    * {company_id: "company_1:score,company_2:score"}, sorted by score high to low
* Get Call
  * Fetches string for company_id, parses out first 10 recs by score, returns list

### Matches
* Likes DDB: primary key company_id_1:type, value: company_id_2 where value is who they like
* Startup clicks like on a VC in recs:
  * Call to core service:
    * POST to company 1, company 2, likes

### Messaging Service [1 week]
* Requirement: User authentication must be complete
* Chime SDK
  * https://aws.amazon.com/blogs/business-productivity/build-chat-features-into-your-application-with-amazon-chime-sdk-messaging/
  * https://docs.aws.amazon.com/chime/latest/dg/using-the-messaging-sdk.html
  * https://aws.amazon.com/blogs/business-productivity/quickly-launch-an-amazon-chime-sdk-application-with-aws-amplify/

### Notifications
* Once actioned, we remove from notification tray
* Types:
  * Messages
  * Matches
  * Company is Interested
  * Marketing
  * Account notifications
* Storage: DDB
  * primary key
    * user_id
    * notification_id
  * sort_key
  * set 30 day retention policy
* Lambda
  * GET
    * Lambda that takes in user_id, token
    * Gets most recent ten notifications
    * Returns in JSON format
  * BACKEND POST will get triggered by backend services
    * i.e recs are ready, account notification
    * user_id, notification_type, notification_body
  * CLIENT POST 
    * messages, matches
    * from_user_id, user_id, notification_type, notification_body
* Later:
  * States: Unread, Read, Actioned
  * Push notifications
  * Caching on site load instead of notification load
### Resources
* Dynamo DB:
  * https://docs.aws.amazon.com/amazondynamodb/latest/developerguide/HowItWorks.CoreComponents.html
  * https://www.codurance.com/publications/2019/02/25/dynamodb-explained-part-1

