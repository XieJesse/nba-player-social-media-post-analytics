import psycopg

with psycopg.connect("dbname=project1 user=postgres password=postgres") as conn:
    # print("test")
    with conn.cursor() as cur:
        # print("test")

        delete_player_posts_table = """
            DROP TABLE IF EXISTS player_posts ;
        """
        cur.execute(delete_player_posts_table)
        
        delete_players_table = """
            DROP TABLE IF EXISTS players ;
        """
        cur.execute(delete_players_table)

        delete_posts_table = """
            DROP TABLE IF EXISTS posts ;
        """
        cur.execute(delete_posts_table)

        
        conn.commit()