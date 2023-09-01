import os

def delete_content_from_word_doc(file_path):
    os.remove(file_path)
    # Create a new empty Word document
    doc = docx.Document("clear.docx")

    # Save the new empty document, effectively replacing the original one
    doc.save(file_path)


delete_content_from_word_doc("speakingTest.docx")