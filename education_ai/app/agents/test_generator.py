from crewai import Agent
from pydantic import Field

class TestGenerator(Agent):
    grade: int = Field(description="The grade level")
    subject: str = Field(description="The subject")
    chapters: list = Field(description="List of chapters")

    def __init__(self, grade: int, subject: str, chapters: list, llm, raw_documents):
        super().__init__(
            role="Test Generator",
            goal=f"Create challenging and fair multiple-choice questions for {subject} in Class {grade}",
            backstory=f"You are an experienced {subject} exam creator for Class {grade}",
            allow_delegation=False,
            llm=llm,
            grade=grade,
            subject=subject,
            chapters=chapters,
            raw_documents=raw_documents
        )

    def execute(self, task_description: str) -> str:
        num_questions = int(task_description.split("Generate ")[-1].split(" questions")[0])
        
        # Filter documents for the selected chapters only
        chapter_docs = [doc for doc in self.raw_documents if doc.metadata['chapter'] in self.chapters]
        
        if not chapter_docs:
            return f"No content found for the specified chapters in {self.subject} for Class {self.grade}."
        
        # Create a context for each chapter separately
        chapter_contexts = {}
        for doc in chapter_docs:
            chapter = doc.metadata['chapter']
            if chapter not in chapter_contexts:
                chapter_contexts[chapter] = []
            chapter_contexts[chapter].append(doc.page_content)
        
        all_questions = []
        for chapter, context in chapter_contexts.items():
            chapter_content = "\n".join(context)
            prompt = f"""
            Based STRICTLY on the following content from Chapter {chapter} of the textbook, create {num_questions // len(chapter_contexts)} multiple-choice questions for {self.subject} in Class {self.grade}.
            Do not use any information outside of this specific chapter content.
            Include 4 options for each question and indicate the correct answer.
            Do not invent any information that is not present in the given content.
            If there isn't enough information to create the requested number of questions, create as many as possible based on the available content.

            Content:
            {chapter_content[:5000]}  # Limit context to avoid token limits

            Generate questions:
            """
            
            chapter_questions = self.llm.generate(prompt)
            all_questions.append(f"Questions for Chapter {chapter}:\n{chapter_questions}")
        
        return f"Generated questions for {self.subject} in Class {self.grade} based on chapters {', '.join(map(str, self.chapters))}:\n\n" + "\n\n".join(all_questions)