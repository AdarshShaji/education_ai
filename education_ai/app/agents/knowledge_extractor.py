from crewai import Agent
from pydantic import Field

class KnowledgeExtractor(Agent):

    grade: int = Field(description="The grade level")
    subject: str = Field(description="The subject")
    chapters: list = Field(description="List of chapters")

    def __init__(self, grade: int, subject: str, chapters: list, llm, raw_documents):
        super().__init__(
            role="Knowledge Extractor",
            goal=f"Extract and summarize key concepts from {subject} documents for Class {grade}",
            backstory=f"You are a skilled {subject} educator capable of distilling complex information",
            allow_delegation=False,
            llm=llm,
            grade=grade,
            subject=subject,
            chapters=chapters,
            raw_documents=raw_documents
        )

    def execute(self, task_description: str) -> str:
        key_concepts = []
        for chapter in self.chapters:
            # Filter raw documents for the current chapter
            chapter_docs = [doc for doc in self.raw_documents if doc.metadata['chapter'] == chapter]
            context = "\n".join([doc.page_content for doc in chapter_docs])
            
            prompt = f"""
            Based solely on the following content from Chapter {chapter} of {self.subject} for Class {self.grade}, list 5 key concepts.
            Do not invent any information that is not present in the given content.

            Content:
            {context[:10000]}  # Limit context to avoid token limits

            List 5 key concepts:
            """
            
            concepts = self.llm.generate(prompt)
            key_concepts.append(f"Chapter {chapter} Key Concepts:\n{concepts}")
        return "\n\n".join(key_concepts)

