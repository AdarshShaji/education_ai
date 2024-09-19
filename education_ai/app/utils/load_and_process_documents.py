import os
import logging
import fitz  # PyMuPDF
from langchain.schema import Document
import markdown

logging.basicConfig(level=logging.INFO)

def load_and_process_documents(grade, subject, chapters):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    database_dir = os.path.abspath(os.path.join(current_dir, '..', '..', 'database'))
    
    logging.info(f"Database directory: {database_dir}")
    
    documents = []
    grade_dir = os.path.join(database_dir, f"Class_{grade}")
    subject_dir = os.path.join(grade_dir, subject.replace(" ", "_"))
    
    logging.info(f"Looking for documents in directory: {subject_dir}")
    
    if not os.path.exists(database_dir):
        logging.error(f"Database directory does not exist: {database_dir}")
        return [], []

    if not os.path.exists(grade_dir):
        logging.error(f"Grade directory does not exist: {grade_dir}")
        return [], []

    if not os.path.exists(subject_dir):
        logging.error(f"Subject directory does not exist: {subject_dir}")
        return [], []

    chapter_names = []
    
    try:
        for filename in os.listdir(subject_dir):
            logging.info(f"Found file: {filename}")
            if filename.endswith('.md') or filename.endswith('.pdf'):
                chapter_name = filename.split('.')[0].replace('_', ' ')
                chapter_names.append(chapter_name)
                logging.info(f"Added chapter: {chapter_name}")

        logging.info(f"Available chapters: {chapter_names}")
    except Exception as e:
        logging.error(f"Error accessing files in directory {subject_dir}: {str(e)}")
        return [], []

    if not chapter_names:
        logging.warning(f"No chapters found in {subject_dir}")
        return [], []

    for chapter in chapters:
        file_path = os.path.join(subject_dir, f"{chapter.replace(' ', '_')}")
        if os.path.exists(file_path + '.md'):
            documents.extend(process_markdown(file_path + '.md', chapter, subject, grade))
        elif os.path.exists(file_path + '.pdf'):
            documents.extend(process_pdf(file_path + '.pdf', chapter, subject, grade))
        else:
            logging.warning(f"No file found for chapter: {chapter}")

    return documents, chapter_names

def process_pdf(file_path, chapter, subject, grade):
    logging.info(f"Processing PDF file: {file_path}")
    try:
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        
        metadata = {
            'title': doc.metadata.get('title', ''),
            'author': doc.metadata.get('author', ''),
            'chapter': chapter,
            'subject': subject,
            'grade': grade
        }
        
        doc.close()
        logging.info(f"Processed {len(text)} characters from {file_path}")
        return [Document(page_content=text, metadata=metadata)]
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return []

def process_markdown(file_path, chapter, subject, grade):
    logging.info(f"Processing Markdown file: {file_path}")
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            md_content = file.read()
        
        html_content = markdown.markdown(md_content)
        
        metadata = {
            'title': f"Chapter {chapter}",
            'author': 'Unknown',
            'chapter': chapter,
            'subject': subject,
            'grade': grade
        }
        
        logging.info(f"Processed {len(md_content)} characters from {file_path}")
        return [Document(page_content=html_content, metadata=metadata)]
    except Exception as e:
        logging.error(f"Error processing {file_path}: {str(e)}")
        return []