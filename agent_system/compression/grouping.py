def group_by_api_round(messages):
    if not messages:
        return []
    
    groups = []
    current_group = []
    
    for msg in messages:
        current_group.append(msg)
        
        # 每一对 user + assistant 分为一组
        if len(current_group) >= 2 and msg["role"] == "assistant":
            groups.append(current_group)
            current_group = []
    
    if current_group:
        groups.append(current_group)
    
    return groups