import psycopg

with psycopg.connect("dbname=project1 user=postgres password=postgres") as conn:
    # print("test")
    with conn.cursor() as cur:
        # print("test")

        create_players_table = """
            CREATE TABLE IF NOT EXISTS players (
                id serial PRIMARY KEY,
                name VARCHAR(50) UNIQUE NOT NULL,
                total_sentiment_score DOUBLE PRECISION,
                num_posts integer
            );
        """
        cur.execute(create_players_table)
        with open("../players.txt", 'r') as file_object:
            for line in file_object:
                player_name = line.split(",")[0]
                cur.execute(
                    "INSERT INTO players (name, total_sentiment_score, num_posts) VALUES (%s, %s, %s) ON CONFLICT (name) DO NOTHING;",
                    (player_name.replace('\n', ''), 0, 0))
        cur.execute("SELECT * FROM players")
        print(cur.fetchall())

        create_posts_table = """
            CREATE TABLE IF NOT EXISTS posts (
                id serial PRIMARY KEY,
                title VARCHAR(100) NOT NULL,
                platform VARCHAR(50) NOT NULL,
                content VARCHAR(1000),
                url VARCHAR(100) NOT NULL,
                created_time TIMESTAMP,
                json jsonb,
                toxicity_score DOUBLE PRECISION
            );
        """
        

        cur.execute(create_posts_table)

        create_player_posts_table = """
            CREATE TABLE IF NOT EXISTS player_posts (
                player_id INTEGER REFERENCES players(id),
                post_id INTEGER REFERENCES posts(id),
                PRIMARY KEY (player_id, post_id),
                sentiment_score DOUBLE PRECISION
            );
        """
        

        cur.execute(create_player_posts_table)


        conn.commit()