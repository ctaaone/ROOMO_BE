from .db import connect_maindb

# Returns true if reservation success, false otherwise
def user_put_reservation(user_id, space_id, start_time, end_time) :
    user_id = str(user_id)
    space_id = str(space_id)

    # Check if reservation time is available
    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT DISTINCT s.id
                FROM spaces s JOIN reservations r
                ON s.id = r.space_id AND s.id = %s
                WHERE (r.start_time >= %s AND r.start_time < %s) OR (r.end_time > %s AND r.end_time <= %s) OR (r.start_time <= %s AND r.end_time >= %s) ;
                """, (space_id, start_time, end_time, start_time, end_time, start_time, end_time))
    res = cur.fetchall()
    cur.close()
    conn.close()
    if res != [] : return False

    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                INSERT INTO reservations (user_id, space_id, start_time, end_time)
                VALUES (%s, %s, %s, %s);
                """, (user_id, space_id, start_time, end_time))
    conn.commit()
    cur.close()
    conn.close()

    return True

def delete_reservation(resv_id) :
    resv_id = str(resv_id)
    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                DELETE FROM reservations
                WHERE id = %s;
                """, (resv_id,))
    conn.commit()
    cur.close()
    conn.close()

def get_reservations(provider_id) :
    provider_id = str(provider_id)
    from .space import get_space_ids
    space_id = get_space_ids(provider_id=provider_id)[0][0]

    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT id, user_id, start_time, end_time
                FROM reservations
                WHERE space_id = %s
                ORDER BY id DESC;
                """, (space_id,))
    fetch_result = cur.fetchall()
    cur.close()
    conn.close()
    reservation_list = [{"id":r[0], "user_id":r[1], "start_time":r[2], "end_time":r[3]} for r in fetch_result]
    return {"list" : reservation_list}

def user_get_reservation(user_id) :
    user_id = str(user_id)
    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT r.id, r.space_id, r.start_time, r.end_time,
                s.name, s.address, s.abstract, s.space_type, r.user_id
                FROM reservations r
                JOIN spaces s ON r.space_id = s.id
                WHERE r.user_id = %s
                ORDER BY r.id DESC;
                """, (user_id,))
    fetch_result = cur.fetchall()
    cur.close()
    conn.close()

    reservation_list = []
    for r in fetch_result :
         if user_get_review(space_id=r[1], user_id=user_id)["exist"] == 1 : reviewed = 1
         else : reviewed = 0
         reservation_list.append({
            "reservation_id" : r[0],
            "space_id" : r[1],
            "reservation_start_time" : r[2],
            "reservation_end_time" : r[3],
            "space_name" : r[4],
            "space_address": r[5],
            "space_abstract": r[6],
            "space_type": r[7],
            "reviewed": reviewed
        })
    
    return {"list" : reservation_list}

def get_reviews(space_id) :
    space_id = str(space_id)

    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT id, content
                FROM reviews
                WHERE space_id = %s;
                """, (space_id, ))
    fetch_result = cur.fetchall()
    cur.close()
    conn.close()
    return {"list": [{"review_id":e[0], "content":e[1]} for e in fetch_result]}

def user_get_review(space_id, user_id):
    user_id = str(user_id)
    space_id = str(space_id)

    conn = connect_maindb()
    cur = conn.cursor()
    cur.execute("""
                SELECT id, content
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

def put_review(space_id, user_id, content):
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