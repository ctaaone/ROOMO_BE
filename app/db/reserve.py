from .db import connect_maindb

def user_reservation_list(user_id) :
    user_id = str(user_id)
    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT r.id, r.space_id, r.start_time, r.end_time,
                s.name, s.address, s.abstract, s.space_type
                FROM reservations r
                JOIN spaces s ON r.space_id = s.id
                WHERE r.user_id = %s;
                """, (user_id))
    fetch_result = cur.fetchall()
    cur.close()
    conn.close()

    reservation_list = []
    for r in fetch_result :
         reservation_list.append({
            "reservation_id" : r[0],
            "space_id" : r[1],
            "reservation_start_time" : r[2],
            "reservation_end_time" : r[3],
            "space_name" : r[4],
            "space_address": r[5],
            "space_abstract": r[6],
            "space_type": r[7],
        })
    
    return {"list" : reservation_list}

def get_user_review(space_id, user_id):
    user_id = str(user_id)
    space_id = str(space_id)

    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT review_id, content
                FROM reviews
                WHERE user_id = %s AND space_id = %s;
                """, (user_id, space_id))
    fetch_result = cur.fetchall()
    cur.close()
    conn.close()
    
    if len(fetch_result) == 0:
        return {
            "exist" : 0
        } 
    return {
        "exist" : 1,
        "review_id": fetch_result[0][0],
        "content": fetch_result[0][1]
    }

def write_user_review(space_id, user_id, content):
    user_id = str(user_id)
    space_id = str(space_id)

    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                INSERT INTO reviews (user_id, space_id, content)
                VALUES (%s, %s, %s) RETURNING id;
                """, (user_id, space_id, content))
    new_id = cur.fetchone()[0]
    conn.commit()
    cur.close()
    conn.close()

    return new_id