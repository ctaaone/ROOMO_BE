from .db import connect_maindb
from .vectordb import search_near_vector

# Fetch spaces desc_summary, review_summary
def get_space_summary(space_id) :
    space_id = str(space_id)
    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT desc_summary, review_summary
                FROM spaces
                WHERE id = %s
                """, (space_id,))
    desc_summary, review_summary = cur.fetchall()[0]
    cur.close()
    conn.close()
    return (desc_summary, review_summary)

def search_spaces(space_type, resv_start, resv_end, extra_req, user_id) :
    # Fetch spaces that matches type & reservation time
    conn = connect_maindb()
    cur = conn.cursor()

    # TODO ? Add geo search
    # cur.execute("""
    #             SELECT id, name, location, address, abstract, desc_summary
    #             FROM spaces
    #             WHERE ST_DWithin(
    #                 geom,
    #                 ST_SetSRID(ST_MakePoint(%s, %s), 4326)::geography,
    #                 1000
    #             );
    #             """, (longitude, latitude))
    
    if resv_start == "" :
        cur.execute("""
                    SELECT id, name, location, address, abstract, desc_summary, review_summary
                    FROM spaces
                    WHERE space_type = %s
                    """, (space_type,))
    ## Consider available time
    else :
        cur.execute("""
                    SELECT id, name, location, address, abstract, desc_summary, review_summary
                    FROM spaces
                    WHERE space_type = %s AND id NOT IN (
                    SELECT DISTINCT s.id
                    FROM spaces s JOIN reservations r
                    ON s.id = r.space_id
                    WHERE (r.start_time >= %s AND r.start_time < %s) OR (r.end_time > %s AND r.end_time <= %s) OR (r.start_time <= %s AND r.end_time >= %s)
                    );
                    """, (space_type, resv_start, resv_end, resv_start, resv_end, resv_start, resv_end))


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
            "desc_summary": space[5],
            "review_summary": space[6]
        }

    if len(space_list) == 0 :
        return []

    ### Process vector processing (recommend task) ###
    # First extract space ids in list
    space_id_list = [row[0] for row in space_list]
    # Second get user preference (space review summary) from reservation history
    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT s.review_summary
                FROM spaces s
                JOIN reservations r ON r.space_id = s.id
                WHERE r.user_id = %s
                ORDER BY r.id DESC
                LIMIT 3;
                """, (user_id,))
    reserve_list = cur.fetchall()
    cur.close()
    conn.close()
    user_text = ""
    # for r in reserve_list :
    #     user_text += r[0]
    user_text += extra_req
    
    # print("fetch complete : ", user_text, space_id_list)
    # Then pick recommended spaces from list
    if user_text != "" :
        space_recommend_list = search_near_vector(user_text, space_id_list)
    else : space_recommend_list = space_id_list
    # space_recommend_list = space_id_list[:10]

    ret = [space_list_map[key] for key in space_recommend_list]
    return ret

