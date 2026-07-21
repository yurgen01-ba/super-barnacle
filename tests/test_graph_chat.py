import unittest
from types import SimpleNamespace

from ai.graph_answering import stream_project_question_over_graph
from providers.text.factory import create_text_provider


class _Retriever:
    def retrieve(self, question):
        return SimpleNamespace(context="Project context", intent="summary", stats={})


class _StreamingProvider:
    def __init__(self):
        self.prompt = ""

    def stream(self, prompt):
        self.prompt = prompt
        yield "Hello"
        yield " world"


class GraphChatTests(unittest.TestCase):
    def test_graph_answer_is_streamed_chunk_by_chunk(self):
        provider = _StreamingProvider()

        chunks = list(
            stream_project_question_over_graph(
                "Describe the project",
                text_provider=provider,
                graph_retriever=_Retriever(),
            )
        )

        self.assertEqual(["Hello", " world"], chunks)
        self.assertIn("Project context", provider.prompt)
        self.assertIn("Describe the project", provider.prompt)

    def test_factory_forwards_chat_token_limit(self):
        provider = create_text_provider(num_predict=123)

        self.assertEqual(123, provider.num_predict)


if __name__ == "__main__":
    unittest.main()
