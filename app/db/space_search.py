from .db import connect_maindb
from .vectordb import search_near_vector

def search_spaces(space_type, latitude, longtitude, extra_req, user_id) :
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
    cur.close()
    conn.close()

    # Result space list & map
    space_list_map = {}
    for space in space_list :
        space_list_map[space[0]] = {
            "space_id" : space[0],
            "name" : space[1],
            "location" : space[2],
            "address" : space[3],
            "abstract" : space[4]
        }

    if len(space_list) == 0 :
        return []

    # Process vector processing (recommend task)
    space_id_list = [row[0] for row in space_list]
    space_recommend_list = search_near_vector(user_id, space_id_list)

    # TODO : Additional user requests from space agent


    ret = [space_list_map[sid] for sid in space_recommend_list]
    return ret

