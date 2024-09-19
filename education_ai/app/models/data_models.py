class Subject:
    def __init__(self, name, chapters):
        self.name = name
        self.chapters = chapters

class Teacher:
    def __init__(self, name, subject):
        self.name = name
        self.subject = subject

class ClassInfo:
    def __init__(self, grade, subjects):
        self.grade = grade
        self.subjects = subjects