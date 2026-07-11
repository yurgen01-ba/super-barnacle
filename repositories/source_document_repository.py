from __future__ import annotations

from models.source_document import SourceChunk, SourceDocument


class SourceDocumentRepository:
    """
    Runtime repository for normalized source documents and chunks.

    This does not replace the existing SourceRepository yet.
    It provides a consistent source layer for the new Project Model pipeline.
    """

    def __init__(self):
        self._documents: dict[str, SourceDocument] = {}
        self._chunks: dict[str, SourceChunk] = {}

    def save_document(
        self,
        source_type: str,
        title: str,
        original_text: str,
        project_id: str = "default",
        source_ref: str = "",
        metadata: dict | None = None,
    ) -> SourceDocument:
        document = SourceDocument.create(
            source_type=source_type,
            title=title,
            original_text=original_text,
            project_id=project_id,
            source_ref=source_ref,
            metadata=metadata,
        )
        self._documents[document.id] = document
        return document

    def save_chunks(
        self,
        document: SourceDocument,
        chunks: list[str],
        metadata: dict | None = None,
    ) -> list[SourceChunk]:
        saved_chunks = []

        for index, text in enumerate(chunks, start=1):
            chunk = SourceChunk.create(
                document_id=document.id,
                project_id=document.project_id,
                chunk_no=index,
                text=text,
                metadata=metadata,
            )
            self._chunks[chunk.id] = chunk
            saved_chunks.append(chunk)

        return saved_chunks

    def get_document(self, document_id: str) -> SourceDocument | None:
        return self._documents.get(document_id)

    def list_documents(self, project_id: str = "default") -> list[SourceDocument]:
        return [
            document for document in self._documents.values()
            if document.project_id == project_id
        ]

    def list_chunks(self, document_id: str) -> list[SourceChunk]:
        return sorted(
            [chunk for chunk in self._chunks.values() if chunk.document_id == document_id],
            key=lambda chunk: chunk.chunk_no,
        )


source_document_repository = SourceDocumentRepository()
