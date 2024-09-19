from models.data_models import Subject, Teacher, ClassInfo

CLASSES_CONFIG = {
    1: ClassInfo(1, [
        Subject("Mathematics", ["Numbers", "Basic Arithmetic"]),
        Subject("English", ["Alphabet", "Simple Words"])
    ]),
    2: ClassInfo(2, [
        Subject("Mathematics", ["Addition", "Subtraction"]),
        Subject("Science", ["Plants", "Animals"])
    ]),
    10: ClassInfo(2, [
        Subject("Mathematics", ["Addition", "Subtraction"]),
        Subject("Science", ["Plants", "Animals"]),
        Subject("English", ["A Letter to God", "Nelson Mandela", "Two Stories about Flying", "From The Diary of Anne Frank", "Glimpses of India", "Mijbil The Otter", "Madam Rides the Bus", "The Sermon At Benares", "The Proposal"])
    ]),
}

TEACHERS = [
    Teacher("Mr. Smith", "Mathematics"),
    Teacher("Ms. Johnson", "English"),
    Teacher("Dr. Brown", "Science"),
]