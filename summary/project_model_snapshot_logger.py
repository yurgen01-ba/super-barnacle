from repositories.knowledge_provenance_repository import knowledge_provenance_repository
def save_project_model_snapshot(model, project_id='default'):
    version=getattr(model,'version',0)
    data=model.to_dict() if hasattr(model,'to_dict') else dict(model)
    knowledge_provenance_repository.create(f'project_model:{project_id}:v{version}','project_model','project_model_snapshot',f'Project Model snapshot v{version}',str(data),'project_model:snapshot',project_id,{'version':version})
