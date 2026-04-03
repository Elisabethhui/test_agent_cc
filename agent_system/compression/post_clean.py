from agent_system.compression.micro_compact import CACHE_STATE

def post_compact_cleanup(session_id: str, is_main_thread: bool):
    CACHE_STATE.pending_edits.clear()
    print(f"✅ 清理完成 | session={session_id} | main_thread={is_main_thread}")