from .db import connect_maindb
from .vectordb import search_near_vector

def search_spaces(space_type, latitude, longtitude, user_id) :
    conn = connect_maindb()
    cur = conn.cursor()

    # cur.execute("""
    #             SELECT id, name, location, address, abstract, desc_summary
    #             FROM spaces
    #             WHERE ST_DWithin(
    #                 geom,
    #                 ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
    #                 1000
    #             );
    #             """, (longitude, latitude))

    cur.execute("""
                SELECT id, name, location, address, abstract, desc_summary
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
            "abstract" : space[4],
            "desc_summary": space[5]
        }

    if len(space_list) == 0 :
        return []

    # Process vector processing (recommend task)
    # First extract space ids in list
    space_id_list = [row[0] for row in space_list]

    # TODO : Using vector recommendation
    # space_recommend_list = search_near_vector(user_id, space_id_list)
    # Then pick recommended spaces from list
    space_recommend_list = space_id_list[:10]

    ret = [space_list_map[key] for key in space_recommend_list]
    return ret

