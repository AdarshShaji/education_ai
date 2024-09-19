from agents.document_processor import DocumentProcessor
from agents.knowledge_extractor import KnowledgeExtractor
from agents.question_answerer import QuestionAnswerer
from agents.test_generator import TestGenerator
from agents.concept_explainer import ConceptExplainer
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from config import CLASSES_CONFIG, TEACHERS
from crewai import Crew, Task
from utils.load_and_process_documents import load_and_process_documents
import os
from dotenv import load_dotenv

load_dotenv()

def create_education_crew(grade, subject, selected_chapters, task_type, additional_info=None):
    llm = ChatGoogleGenerativeAI(model="gemini-1.0-pro", google_api_key="AIzaSyDmf0d09V7jGsuN-kfZ6Di-bF0LbCyH7_I", temperature=0.1)

    raw_documents, _ = load_and_process_documents(grade, subject, selected_chapters)
    if not raw_documents:
        st.error("Failed to process documents. Please check the logs for more information.")
        return None
    
    document_processor = DocumentProcessor(grade=grade, subject=subject, chapters=selected_chapters, llm=llm, raw_documents=raw_documents)
    knowledge_extractor = KnowledgeExtractor(grade=grade, subject=subject, chapters=selected_chapters, llm=llm, raw_documents=raw_documents)
    question_answerer = QuestionAnswerer(grade=grade, subject=subject, chapters=selected_chapters, llm=llm, raw_documents=raw_documents)
    test_generator = TestGenerator(grade=grade, subject=subject, chapters=selected_chapters, llm=llm, raw_documents=raw_documents)
    concept_explainer = None

    if task_type == "Explain Concepts":
        concept_explainer = ConceptExplainer(grade=grade, subject=subject, chapters=selected_chapters, concepts=additional_info, llm=llm, raw_documents=raw_documents)
    
    if task_type == "Explain Concepts":
        task = Task(
            description=f"Explain the following concepts for {subject} in Class {grade}, chapters {', '.join(map(str, selected_chapters))}: {', '.join(additional_info)}",
            agent=concept_explainer,
            expected_output=f"Detailed explanations of the concepts: {', '.join(additional_info)} for {subject} in Class {grade}, focusing on the selected chapters"
        )
    elif task_type == "Generate Questions":
        task = Task(
            description=f"Generate {additional_info} questions for {subject} in Class {grade}, chapters {', '.join(map(str, selected_chapters))}",
            agent=test_generator,
            expected_output=f"A set of {additional_info} multiple-choice questions for {subject} in Class {grade}, based on the selected chapters"
        )
    elif task_type == "Answer Queries":
        task = Task(
            description=f"Answer the following question for {subject} in Class {grade}, chapters {', '.join(map(str, selected_chapters))}: {additional_info}",
            agent=question_answerer,
            expected_output=f"A detailed and comprehensive answer to the query: '{additional_info}' for {subject} in Class {grade}, covering all relevant information from the specified chapters"
        )
    else:
        raise ValueError("Invalid task type")
    
    agents = [agent for agent in [document_processor, knowledge_extractor, question_answerer, test_generator, concept_explainer] if agent is not None]

    crew = Crew(
        agents=agents,
        tasks=[task]
    )

    return crew

def main():
    st.title("Educational AI Assistant")

    grade = st.selectbox("Select Class", list(CLASSES_CONFIG.keys()))
    class_info = CLASSES_CONFIG[grade]
    subject_names = [subject.name for subject in class_info.subjects]
    subject = st.selectbox("Select Subject", subject_names)
    selected_subject = next(sub for sub in class_info.subjects if sub.name == subject)
    
    st.info(f"Debug: Looking for documents for Grade {grade}, Subject: {subject}")
    
    # Load available chapters from the database
    _, chapter_names = load_and_process_documents(grade, subject, [])
    
    if not chapter_names:
        st.error(f"No chapters found for Class {grade}, Subject: {subject}. Please check the database directory.")
        st.info("Debug: Check the logs for more information about the directory structure.")
        return

    selected_chapters = st.multiselect("Select Chapters", chapter_names)

    task_type = st.selectbox("What would you like to do?", ["Explain Concepts", "Generate Questions", "Answer Queries"])

    additional_info = None

    if task_type == "Explain Concepts":
        concepts = st.text_input("Enter concepts to explain (comma-separated)")
        additional_info = [c.strip() for c in concepts.split(",")] if concepts else []

    elif task_type == "Generate Questions":
        num_questions = st.number_input("Number of questions", min_value=1, max_value=20, value=5)
        additional_info = num_questions

    elif task_type == "Answer Queries":
        query = st.text_input("Enter your question")
        additional_info = query

    if st.button("Execute Task"):
        if not selected_chapters:
            st.error("Please select at least one chapter.")
            return

        st.info(f"Processing documents for Grade {grade}, Subject: {subject}, Chapters: {selected_chapters}")
        crew = create_education_crew(grade, subject, selected_chapters, task_type, additional_info)
        if crew is not None:
            result = crew.kickoff()
            st.subheader("Result")
            st.write(result)
        else:
            st.error("Failed to create the education crew. Please check the logs for more information.")
            st.info("Debug Info:")
            st.write(f"Grade: {grade}")
            st.write(f"Subject: {subject}")
            st.write(f"Chapters: {selected_chapters}")

if __name__ == "__main__":
    main()