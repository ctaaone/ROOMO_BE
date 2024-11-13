from openai import OpenAI
import re, os, json
from .roles import useragent_main_role, useragent_request_role, useragent_recommend_role
from db import search_spaces

client = OpenAI()
user_conversation_history = []
provider_conversation_history = []

def get_gpt(conversation, role, user_content="") :
    if user_content is not "" :
        conversation.append({"role": "user", "content": user_content})
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation + {"role": "system", "content": role}
    )
    ret = response.choices[0].message
    conversation.append({"role": "assistant", "content": ret})
    return ret


def useragent_main(content, tries, user_id):
    
    # Restart threshold
    if tries > 5 :
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
                space_lati = tokens[2]
                space_longti = tokens[3]
                extra_req = tokens[4]

                # Get spaces from db sorted by user preference vector
                space_list = search_spaces(space_type, space_lati, space_longti, user_id=user_id)
                
                # Select space based on extra request by user agent
                if extra_req == "" : extra_req = "없음"
                space_agent_query = "공간 후보 목록 :\n" + json.dumps(space_list) + "사용자 요청 :\n" + extra_req
                user_conversation_history.append({"role": "assistant", "content": space_agent_query})
                res_str = get_gpt(conversation=user_conversation_history, role=useragent_recommend_role)
                 
                # Parsing agent response and space list
                res_space_id_list = [int(num) for num in re.search(r'\[(.*?)\]', res_str)]
                agent_res = res_str[:res_str.find('[')]
                res_space_list = [space_list[key] for key in res_space_id_list]

                if len(res_space_list) == 0:
                    user_conversation_history.append({"role": "assistant", "content": "조건에 맞는 공간이 없습니다."})
                    return {"type": "text", "content": "조건에 맞는 공간이 없습니다." }
                else :
                    user_conversation_history.append({"role": "assistant", "content": agent_res+json.dumps(res_space_list)})
                    return {"type": "spaceList", "content": agent_res, "list": json.dumps(res_space_list)}

            # Space reservation
            elif "TYPE2" in tokens[0] :
                None

            # Space inquiry
            elif "TYPE3" in tokens[0] :
                None
            
            # Not in case, error
            else :
                raise Exception('Out of cases')
            
        except Exception as e :
            print(f"Error calling ChatGPT API in proces: {e}")
            print("Retry useragent_main")
            user_conversation_history = conversation_backup
            useragent_main(content, tries+1)
