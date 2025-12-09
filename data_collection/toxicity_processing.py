from googleapiclient import discovery
from googleapiclient.errors import HttpError

import json
import time
import psycopg

import os 

client = discovery.build(
    "commentanalyzer",
    "v1alpha1",
    developerKey=os.getenv("PERSPECTIVE_API_KEY"),
    discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
    static_discovery=False,
)

with psycopg.connect("dbname=project1 user=postgres password=postgres") as conn:
    with conn.cursor() as cur:
        
        select_rows_default_values_query = """
            SELECT id, content FROM posts
            WHERE toxicity_score IS NULL OR toxicity_score = 0.0;
        """
        cur.execute(select_rows_default_values_query)
        posts = cur.fetchall()

        for i, (post_id, content) in enumerate(posts):
            analyze_request = {
                'comment': {'text': content},
                'requestedAttributes': {'TOXICITY': {}}
            }

            try:
                toxicity_score = .01
                if content:
                  response = client.comments().analyze(body=analyze_request).execute()
                  toxicity_score = response["attributeScores"]["TOXICITY"]["summaryScore"]["value"]

                cur.execute("""
                    UPDATE posts
                    SET toxicity_score = %s
                    WHERE id = %s;
                """, (toxicity_score, post_id))
                if i % 10 == 0:
                    conn.commit()
                    print(f"{i} rows committed so far")

                print(f"{i} post {post_id}, toxicity {toxicity_score}")
            except HttpError as e:
                print(f"error on post withh {post_id}: {e}")

                cur.execute("""
                    UPDATE posts
                    SET toxicity_score = %s
                    WHERE id = %s;
                """, (0.01, post_id))
                if i % 10 == 0:
                    conn.commit()
                    print(f"{i} rows committed so far")

                print(f"{i} post {post_id}, toxicity {toxicity_score}")

                time.sleep(3)

            time.sleep(1)

        conn.commit()