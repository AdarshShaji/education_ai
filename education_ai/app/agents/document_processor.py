from crewai import Agent
from utils.load_and_process_documents import load_and_process_documents
from pydantic import Field

class DocumentProcessor(Agent):

    grade: int = Field(description="The grade level")
    subject: str = Field(description="The subject")
    chapters: list = Field(description="List of chapters")

    def __init__(self, grade: int, subject: str, chapters: list, llm, raw_documents):
        super().__init__(
            role="Document Processor",
            goal=f"Process and prepare documents for {subject} in Class {grade}",
            backstory=f"You are an expert in handling educational documents for {subject}",
            allow_delegation=False,
            llm=llm,
            grade=grade,
            subject=subject,
            chapters=chapters,
            raw_documents=raw_documents
        )

    def execute(self, task_description: str) -> str:
        summary = f"Processed {len(self.chapters)} chapters for {self.subject} in Class {self.grade}\n"
        for chapter in self.chapters:
            chapter_docs = [doc for doc in self.raw_documents if doc.metadata['chapter'] == chapter]
            if chapter_docs:
                chapter_content = chapter_docs[0].page_content
                chapter_metadata = chapter_docs[0].metadata
                
                prompt = f"""
                Summarize the key points of Chapter {chapter} in {self.subject} for Class {self.grade}.
                
                Content: {chapter_content[:500]}...
                
                Metadata:
                Title: {chapter_metadata.get('title')}
                Author: {chapter_metadata.get('author')}
                """
                
                chapter_summary = self.llm.generate(prompt)
                summary += f"\nChapter {chapter} Summary:\n{chapter_summary}\n"
            else:
                summary += f"\nNo content found for Chapter {chapter}\n"
        return summary

__all__ = ['DocumentProcessor']