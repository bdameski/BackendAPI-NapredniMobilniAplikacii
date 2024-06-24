from PIL import Image
import pytesseract
from database import SessionLocal, Student, ImageRecord
from sqlalchemy.orm import Session
from fpdf import FPDF



def image_to_text(image_path: str, report_id:int):
	"""Function that opens the image, detects names on the image and filters the names with the database

	Args:
		image_path (str): the path of the image
		report_id (int): the id of the report
	"""
	
	db = SessionLocal()

	# opens the image
	img = Image.open(f'{image_path}')

	# Uses tesseract to read the image into a text and convert into a list
	text = pytesseract.image_to_string(img, lang="mkd")
	names = text.split("\n")
	names.pop(-1)  # Remove the last empty element (end line character)

	result = []
	# Loop throgh the names and filter against the databes
	for name in names:
		print(name)
		is_present = db.query(Student).filter(Student.name == name.strip()).first() is not None
		result.append({"name": name.strip(), "is_present": is_present})

	# Generate PDF object with title and insert the names and attendance into the file
	pdf = FPDF()
	pdf.add_page()
 # Add Arial Unicode font
	pdf.add_font("ArialUnicode", "", "arialuni.ttf", uni=True)
	pdf.set_font("ArialUnicode", size=12)
	pdf.cell(200, 10, txt="Name Presence Report", ln=True, align='C')
	for entry in result:
		if entry["name"]:
			status = "Present" if entry["is_present"] else "Not Present"
			pdf.cell(200, 10, txt=f"Name: {entry['name']}, Status: {status}", ln=True)

	# Save the PDF File
	pdf.output(f"files/output_report_{report_id}.pdf")
	# Update the DB
	report = db.query(ImageRecord).filter(ImageRecord.id == report_id).first()
	report.file_url = f"files/output_report_{report_id}.pdf"
	report.status="finished"
	db.commit()
