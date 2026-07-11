class ProjectBrainError(Exception):
    pass


class PipelineError(ProjectBrainError):
    pass


class RepositoryError(ProjectBrainError):
    pass


class ProviderError(ProjectBrainError):
    pass

