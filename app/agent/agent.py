from openai import OpenAI
import re, os, json
from .roles import useragent_main_role, useragent_request_role, useragent_recommend_role
from .roles import useragent_reservation_role, useragent_inquiry_role
from .roles import provider_inquiry_role
from db import search_spaces, user_put_reservation, get_space_summary
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
user_conversation_history = []
provider_conversation_history = {}

def get_gpt(conversation, role, user_content="") :
    if user_content != "" :
        conversation.append({"role": "user", "content": user_content})
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": role}] + conversation
    )
    ret = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": ret})
    return ret

def useragent_main(content, tries, user_id):
    global user_conversation_history
    global provider_conversation_history

    # Restart threshold
    if tries > 2 :
        return "에러 발생, 다시 시도해 주십시오."
    conversation_backup = list(user_conversation_history)

    try:
        # Determine task type from user prompt
        res = get_gpt(
            conversation=user_conversation_history,
            role=useragent_main_role,
            user_content=content)
    except Exception as e:
        print(f"Error calling ChatGPT API: {e}")
        return "Error in ChatGPT API call."
    
    print("Main agent result : ", res)

    # Request additional information to user
    if "!request!" in res :
        res = get_gpt(conversation=user_conversation_history,
                      role=useragent_request_role)
        return {"type": "text", "content": res}
    
    # Or do task
    else :
        tokens = re.findall(r'\[(.*?)\]', res)
        try :
            # Space search
            if "TYPE1" in tokens[0] :
                space_type = tokens[1]
                resv_start = tokens[2]
                resv_end = tokens[3]
                extra_req = tokens[4]

                ## Get spaces from db sorted by user preference vector ##
                space_list = search_spaces(space_type, resv_start, resv_end, extra_req, user_id=user_id)
                print("Space vector filetering complete : ", [{"space_id":e["space_id"], "name":e["name"]} for e in space_list])            
                if space_list == [] :
                    user_conversation_history.append({"role": "assistant", "content": "조건에 맞는 공간이 없습니다."})
                    return {"type": "text", "content": "조건에 맞는 공간이 없습니다." }

                ## Select space based on extra request by user agent ##
                if extra_req == "" : extra_req = "없음"
                space_agent_query = "공간 후보 목록 :\n" + json.dumps(space_list, ensure_ascii=False) + "사용자 요청 :\n" + extra_req
                user_conversation_history.append({"role": "assistant", "content": space_agent_query})
                res_str = get_gpt(conversation=user_conversation_history, role=useragent_recommend_role)
                
                print("Agent's final choices : ", res_str)
                print(re.findall(r'\[///(\d+(?:\s\d+)*)///\]', res_str)[0].split())

                ## Parsing agent response and space list ##
                res_space_id_list = [int(num) for num in re.findall(r'\[///(\d+(?:\s\d+)*)///\]', res_str)[0].split()]
                agent_res = res_str[:res_str.find('[///')]
                res_space_list = [e for e in space_list if e["space_id"] in res_space_id_list]

                if len(res_space_list) == 0:
                    user_conversation_history.append({"role": "assistant", "content": "조건에 맞는 공간이 없습니다."})
                    return {"type": "text", "content": "조건에 맞는 공간이 없습니다." }
                else :
                    user_conversation_history.append({"role": "assistant", "content": agent_res+json.dumps(res_space_list, ensure_ascii=False)})
                    return {"type": "spaceList", "content": agent_res, "list": json.dumps(res_space_list, ensure_ascii=False)}

            # Space reservation
            elif "TYPE2" in tokens[0] :
                space_id = tokens[1]
                start_time = tokens[2]
                end_time = tokens[3]
                reserve_res = user_put_reservation(space_id=space_id, user_id=user_id, start_time=start_time, end_time=end_time)
                if reserve_res is True :
                    user_conversation_history.append({"role": "assistant", "content": f"공간id {space_id}에 대해 {start_time}부터 {end_time}의 예약에 성공했습니다."})
                else :
                    user_conversation_history.append({"role": "assistant", "content": "다른 예약이 있어 예약에 실패했습니다."})
                return {"type": "text", "content": get_gpt(user_conversation_history, useragent_reservation_role) }

            # Space inquiry
            elif "TYPE3" in tokens[0] :
                space_id = int(tokens[1])
                inquiry = tokens[2]
                desc_summary, review_summary = get_space_summary(space_id)
                
                # Check space agent exists, otherwise create
                if space_id not in provider_conversation_history :
                    provider_conversation_history[space_id] = [{"role": "assistant", "content": f"공간에 대한 정보 :\n{desc_summary}\n 리뷰 요약 :\n{review_summary}"},]
                else :
                    provider_conversation_history[space_id][0] = {"role": "assistant", "content": f"공간에 대한 정보 :\n{desc_summary}\n 리뷰 요약 :\n{review_summary}"}
                
                ## Get answer from provider agent
                provider_answer = get_gpt(conversation=provider_conversation_history[space_id], role=provider_inquiry_role, user_content=f"익명의 사용자 문의 : {inquiry}")
                print("Answer from provider agent: ", provider_answer)
                user_conversation_history.append({"role": "assistant", "content": "공간 제공자로부터의 답변 :\n" + provider_answer})
                
                return { "type": "text", "content": get_gpt(conversation=user_conversation_history, role=useragent_inquiry_role) }
            
            # Not in case, error
            else :
                raise Exception('Out of cases')
            
        except Exception as e :
            print(f"Error calling ChatGPT API in proces: {e}")
            print("Retry useragent_main")
            user_conversation_history = conversation_backup
            return useragent_main(content, tries+1, user_id)

def clear_user_history() :
    global user_conversation_history
    user_conversation_history = []
def clear_provider_history() :
    global provider_conversation_history
    provider_conversation_history = {}