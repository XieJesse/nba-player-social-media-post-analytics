import psycopg

with psycopg.connect("dbname=project1 user=postgres password=postgres") as conn:
    # print("test")
    with conn.cursor() as cur:
        # cur.execute("SELECT * FROM posts")
        cur.execute("SELECT * FROM players")
        print(cur.fetchall())
        print()
        cur.execute("SELECT * FROM player_posts")
        # print(cur.fetchall())
        print()
        cur.execute("SELECT COUNT(*) FROM player_posts")
        print(cur.fetchall())


        with cur.copy("COPY players TO STDOUT WITH CSV HEADER") as copy:
            with open("players.csv", "w") as f:
                for data in copy:
                    f.write(bytes(data).decode())

        with cur.copy("COPY player_posts TO STDOUT WITH CSV HEADER") as copy:
            with open("player_posts.csv", "w") as f:
                for data in copy:
                    f.write(bytes(data).decode())

        with cur.copy("COPY posts TO STDOUT WITH CSV HEADER") as copy:
            with open("posts.csv", "w") as f:
                for data in copy:
                    f.write(bytes(data).decode())