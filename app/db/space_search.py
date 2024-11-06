from db import connect_maindb


def search_spaces(space_type, latitude, longtitude, user_id) :
    conn = connect_maindb()
    cur = conn.cursor()

    # cur.execute("""
    #             SELECT id, name, latitude, longitude
    #             FROM spaces
    #             WHERE ST_DWithin(
    #                 geom,
    #                 ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
    #                 1000
    #             );
    #             """, (longitude, latitude))

    cur.execute("""
                SELECT id, name, location, address, abstract
                FROM spaces
                WHERE space_type = %s
                """, (space_type))
    space_list = cur.fetchall()

    if len(space_list) == 0 :
        return -1

    space_id_list = [row[0] for row in space_list]

