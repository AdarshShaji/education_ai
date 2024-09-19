from crewai import Agent
from pydantic import Field

class QuestionAnswerer(Agent):
    grade: int = Field(description="The grade level")
    subject: str = Field(description="The subject")
    chapters: list = Field(description="List of chapters")

    def __init__(self, grade: int, subject: str, chapters: list, llm, raw_documents):
        super().__init__(
            role="Comprehensive Subject Expert and Question Solver",
            goal=f"Provide accurate answers to questions related to {subject} for Class {grade}, based strictly on the provided content",
            backstory=f"You are a {subject} educator for Class {grade}, with access to specific chapter content. You only provide information from the given materials.",
            allow_delegation=False,
            llm=llm,
            grade=grade,
            subject=subject,
            chapters=chapters,
            raw_documents=raw_documents
        )

    def execute(self, task_description: str) -> str:
        query = task_description.split("Question: ")[-1]
        relevant_docs = [doc for doc in self.raw_documents if doc.metadata['chapter'] in self.chapters]
        context = "\n".join([f"Chapter {doc.metadata['chapter']}:\n{doc.page_content}" for doc in relevant_docs])

        prompt = f"""
        Based STRICTLY on the following content from the selected chapters, answer the question for {self.subject} in Class {self.grade}.
        Only use information from these specific chapters: {', '.join(map(str, self.chapters))}.
        Do not use any external knowledge or make up information.
        If the answer is not in the provided content, say "I don't have enough information to answer this question based on the given content from the selected chapters."

        Content:
        {context[:10000]}

        Question: {query}

        Answer:
        """

        answer = self.llm.generate(prompt)
        return f"Question: {query}\n\nAnswer: {answer}"