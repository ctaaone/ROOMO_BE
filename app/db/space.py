from .db import connect_maindb
from .vectordb import search_near_vector, update_space_property
from .reservation import get_reviews

# Get & Update space info for providers
def provider_get_space(provider_id) :
    provider_id = str(provider_id)
    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT name, address, description, space_type, price, capacity
                FROM spaces
                WHERE provider_id = %s
                """, (provider_id,))
    # Fetch only one for now
    res_space = cur.fetchall()[0]
    cur.close()
    conn.close()
    return {
        "name":res_space[0],
        "address":res_space[1],
        "description":res_space[2],
        "space_type":res_space[3],
        "price":res_space[4],
        "capacity":res_space[5]
    }

def provider_update_space(provider_id, space) :
    provider_id = str(provider_id)
    # Update only one for now
    space_id = str(get_space_ids(provider_id=provider_id)[0])

    ### Summarize & embedding update
    conv1 = [{"role": "system", "content": "주어진 공간 설명을 평문으로 정리해줘. 공간 설명에 관련된 내용들은 모두 포함하고, 그렇지 않은 내용은 포함하지 마. 길어도 괜찮음. 요약 과정 등 미사여구는 생략하고 요약 결과만 출력해."}]
    conv2 = [{"role": "system", "content": "주어진 공간 리뷰들을 요약해서 어떤 공간인지 간략히 설명해줘. 요약 과정 등 미사여구는 생략하고 요약 결과만 출력해."}]
    conv3 = [{"role": "system", "content": "주어진 공간 설명과 리뷰를 요약해서 3줄정도로 해당 공간이 어떤 공간인지 요약해줘. ~입니다체를 사용해. 요약 과정 등 미사여구는 생략하고 요약 결과만 출력해."}]
    reviews = get_reviews(space_id=space_id)
    from agent import get_gpt
    desc_summary = get_gpt(content=space["description"], conv=conv1)
    review_summary = get_gpt(content='\n'.join(reviews), conv=conv2)
    abstract = get_gpt(content=space["description"] + '\n리뷰 목록\n' + '\n'.join(reviews), conv=conv3)
    update_space_property(space_id=space_id, text=desc_summary+review_summary)

    ### Update main db
    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                UPDATE spaces
                SET name = %s, address = %s, description = %s, space_type = %s, price = %s, capacity = %s, 
                desc_summary = %s, review_summary = %s, abstract = %s
                WHERE id = %s
                """, (space["name"], space["address"], space["description"], space["space_type"], str(space["price"]), str(space["capacity"]),
                      desc_summary, review_summary, abstract, space_id,))
    conn.commit()
    cur.close()
    conn.close()
    return {}

#


# Fetch all space ids
def get_space_ids(provider_id) :
    provider_id = str(provider_id)
    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT id
                FROM spaces
                WHERE provider_id = %s
                """, (provider_id,))
    space_ids = cur.fetchall()
    cur.close()
    conn.close()
    return space_ids

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

