from crewai import Agent
from pydantic import Field

class ConceptExplainer(Agent):
    grade: int = Field(description="The grade level")
    subject: str = Field(description="The subject")
    chapters: list = Field(description="List of chapters")
    concepts: list = Field(description="List of specific concepts to explain")

    def __init__(self, grade: int, subject: str, chapters: list, concepts: list, llm, raw_documents):
        super().__init__(
            role="Concept Explainer",
            goal=f"Provide clear and detailed explanations of {subject} concepts for Class {grade}",
            backstory=f"You are an expert at breaking down complex {subject} ideas",
            allow_delegation=False,
            llm=llm,
            grade=grade,
            subject=subject,
            chapters=chapters,
            concepts=concepts,
            raw_documents=raw_documents
        )

    def execute(self, task_description: str) -> str:
        explanations = []
        for concept in self.concepts:
            # Filter documents for the selected chapters only
            chapter_docs = [doc for doc in self.raw_documents if doc.metadata['chapter'] in self.chapters]
            
            # Find relevant content for the concept within the selected chapters
            relevant_docs = [doc for doc in chapter_docs if concept.lower() in doc.page_content.lower()]
            context = "\n".join([doc.page_content for doc in relevant_docs[:3]])  # Use top 3 most relevant chunks

            if not context:
                explanations.append(f"Concept: {concept}\nExplanation: No relevant information found for this concept in the selected chapters.")
                continue

            prompt = f"""
            Based solely on the following content from the textbook for {self.subject} in Class {self.grade}, explain the concept of '{concept}', 
            focusing only on chapters {', '.join(map(str, self.chapters))}.
            Do not invent any information that is not present in the given content.
            If the concept is not clearly explained in the provided content, state that there isn't enough information.

            Content:
            {context[:10000]}  # Limit context to avoid token limits

            Provide a clear, concise, and accurate explanation of '{concept}' suitable for the grade level, using only the information provided above:
            """

            explanation = self.llm.generate(prompt)
            explanations.append(f"Concept: {concept}\nExplanation: {explanation}")
        
        return "\n\n".join(explanations)