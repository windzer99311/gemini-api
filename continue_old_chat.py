import json,re

# The target URL with the new query parameters map
def get_chat_resume_setting(session,action_token,conversation_id):
    url = "https://gemini.google.com/_/BardChatUi/data/batchexecute"
    params = {
        "rpcids": "hNvQHb",
        "source-path": f"/app/{conversation_id}",
        "bl": "boq_assistant-bard-web-server_20260716.08_p0",
        "f.sid": "-8622880166764394923",
        "hl": "en-GB",
        "_reqid": "2006650",
        "rt": "c"
    }

    # The active application parameters sent in the body
    data = {
        "f.req": f'[[["hNvQHb","[\\"c_{conversation_id}\\",10,null,1,[1],[4],null,1]",null,"generic"]]]',
        "at": action_token.get("at")
    }

    # Execution step
    response = session.post(url, params=params, data=data,verify=False)
    print(f"Status Code: {response.status_code}")
    print()
    return parse_response_ids(response.text)

def parse_response_ids(raw_payload: str):
    # 1. Clean XSSI header
    cleaned_text = raw_payload.strip()
    if cleaned_text.startswith(")]}'"):
        cleaned_text = cleaned_text[4:].strip()

    # 2. Remove the very first chunk size number (e.g., '2159\n')
    cleaned_text = re.sub(r'^\d+\s*', '', cleaned_text)

    # 3. Split by trailing chunk boundaries to isolate the main JSON block
    json_chunks = re.split(r'\n\d+\n', cleaned_text)
    main_json_str = json_chunks[0].strip()

    conversation_c_id = None
    first_r_id = None
    choice_rc_id = None

    try:
        data = json.loads(main_json_str)
        for item in data:
            if isinstance(item, list) and len(item) >= 3 and item[0] == "wrb.fr":
                inner_raw = item[2]
                if not inner_raw:
                    continue

                inner_data = json.loads(inner_raw)

                if isinstance(inner_data, list) and len(inner_data) > 0:
                    # inner_data[0] is the list of conversational turns
                    turns = inner_data[0]

                    if isinstance(turns, list) and len(turns) > 0:
                        # turns[0] is the CURRENT turn block
                        current_turn = turns[0]

                        if isinstance(current_turn, list):
                            # 1. Extract Conversation c_ ID and First r_ ID: current_turn[0]
                            if len(current_turn) > 0 and isinstance(current_turn[0], list):
                                header_pair = current_turn[0]

                                # c_ ID is at index 0
                                if len(header_pair) > 0:
                                    c_candidate = header_pair[0]
                                    if isinstance(c_candidate, str) and c_candidate.startswith("c_"):
                                        conversation_c_id = c_candidate

                                # r_ ID is at index 1
                                if len(header_pair) > 1:
                                    r_candidate = header_pair[1]
                                    if isinstance(r_candidate, str) and r_candidate.startswith("r_"):
                                        first_r_id = r_candidate

                            # 2. Extract Choice rc_ ID: current_turn[3][0][0][0]
                            if len(current_turn) > 3 and isinstance(current_turn[3], list) and len(current_turn[3]) > 0:
                                level1 = current_turn[3][0]
                                if isinstance(level1, list) and len(level1) > 0:
                                    level2 = level1[0]
                                    if isinstance(level2, list) and len(level2) > 0:
                                        rc_candidate = level2[0]
                                        if isinstance(rc_candidate, str) and rc_candidate.startswith("rc_"):
                                            choice_rc_id = rc_candidate

    except Exception as e:
        print(f"Failed to parse payload: {e}")

    return {
        "c_id": conversation_c_id,
        "r_id": first_r_id,
        "rc_id": choice_rc_id
    }

