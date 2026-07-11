from repositories.knowledge_provenance_repository import knowledge_provenance_repository
def save_transcript_provenance(file_name, source, segment_no, total_segments, raw_text, clean_text, project_id='default', metadata=None):
    source_id=f'{source}:segment:{segment_no}'
    meta={**(metadata or {}),'segment_no':segment_no,'total_segments':total_segments,'file_name':file_name}
    knowledge_provenance_repository.create(source_id,'meeting_transcript_segment','raw_transcript_segment',f'{file_name} — raw transcript segment {segment_no}/{total_segments}',raw_text,'transcription:raw',project_id,meta)
    knowledge_provenance_repository.create(source_id,'meeting_transcript_segment','clean_transcript_segment',f'{file_name} — clean transcript segment {segment_no}/{total_segments}',clean_text,'transcription:clean',project_id,meta)
    return source_id
