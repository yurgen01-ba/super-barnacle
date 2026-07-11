from __future__ import annotations

from ai.graph_prompt_builder import build_graph_prompt
from graph.graph_retriever_v2 import GraphRetrieverV2


class GraphArtifactBuilder:
    """
    Builds artifacts from Project Graph context instead of RAG chunks.
    """

    def __init__(self, graph_retriever: GraphRetrieverV2 | None = None):
        self.graph_retriever = graph_retriever or GraphRetrieverV2()

    def build_prompt(self, artifact_type: str, instruction: str) -> str:
        retrieved = self.graph_retriever.retrieve(instruction)

        artifact_instruction = f"""
Generate artifact type: {artifact_type}

Artifact instruction:
{instruction}

Use the Project Graph context.
Do not use unrelated assumptions.
""".strip()

        return build_graph_prompt(
            question=artifact_instruction,
            graph_context=retrieved.context,
        )

    def generate(self, artifact_type: str, instruction: str, text_provider=None) -> str:
        prompt = self.build_prompt(artifact_type=artifact_type, instruction=instruction)

        if text_provider is None:
            text_provider = self._get_default_text_provider()

        if text_provider is None:
            return prompt

        for method_name in ["generate", "complete", "ask", "invoke"]:
            method = getattr(text_provider, method_name, None)
            if callable(method):
                try:
                    return method(prompt)
                except TypeError:
                    try:
                        return method(prompt=prompt)
                    except Exception:
                        continue
                except Exception:
                    continue

        return prompt

    @staticmethod
    def _get_default_text_provider():
        try:
            from providers.text.factory import get_text_provider
            return get_text_provider()
        except Exception:
            pass

        try:
            from providers.text.factory import create_text_provider
            return create_text_provider()
        except Exception:
            return None
