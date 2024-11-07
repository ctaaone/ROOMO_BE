from openai import OpenAI
import re, os, json
from .roles import useragent_main_role, useragent_request_role
from db import search_spaces

client = OpenAI()
user_conversation_history = [{"role": "system", "content": useragent_main_role}]
provider_conversation_history = []

def get_gpt(conversation, role, content="") :
    if content is not "" :
        conversation.append({"role": "user", "content": content})
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=conversation
    )
    ret = response.choices[0].message
    conversation.append({"role": "assistant", "content": ret})
    return ret

def useragent_main(content, tries):
    if tries > 5 :
        return "에러 발생, 다시 시도해 주십시오."
    conversation_backup = list(user_conversation_history)

    try:
        res = get_gpt(
            conversation=user_conversation_history,
            role=useragent_main_role,
            content=content)
    except Exception as e:
        print(f"Error calling ChatGPT API: {e}")
        return "Error in ChatGPT API call."
    
    # Request additional information from user
    if "!request!" in res :
        res = get_gpt(conversation=user_conversation_history,
                      role=useragent_request_role)
        return {"type": "text", "content": res}
    # Do task
    else :
        tokens = re.findall(r'\[(.*?)\]', res)
        try :
            # Space search
            if "TYPE1" in tokens[0] :
                space_type = tokens[1]
                space_lati = tokens[2]
                space_longti = tokens[3]
                extra_req = tokens[4]

                res_space_list = search_spaces(space_type, space_lati, space_longti, extra_req, user_id=0)

                if len(res_space_list) == 0:
                    user_conversation_history.append({"role": "assistant", "content": "조건에 맞는 공간이 없습니다."})
                    return {"type": "text", "content": "조건에 맞는 공간이 없습니다." }
                else :
                    user_conversation_history.append({"role": "assistant", "content": json.dumps(res_space_list)})
                    return {"type": "spaceList", "content": json.dumps(res_space_list)}

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



