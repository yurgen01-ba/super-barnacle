from repositories.knowledge_provenance_repository import knowledge_provenance_repository
def save_reasoning_snapshot(question, reasoning_context, prompt, answer=None, project_id='default'):
    source_id=f'chat:{abs(hash(question))}'
    knowledge_provenance_repository.create(source_id,'chat','reasoning_context',f'Reasoning context — {question[:80]}',reasoning_context,'chat:reasoning_context',project_id,{'question':question})
    knowledge_provenance_repository.create(source_id,'chat','final_prompt',f'Final prompt — {question[:80]}',prompt,'chat:prompt',project_id,{'question':question})
    if answer is not None:
        knowledge_provenance_repository.create(source_id,'chat','final_answer',f'Final answer — {question[:80]}',answer,'chat:answer',project_id,{'question':question})
