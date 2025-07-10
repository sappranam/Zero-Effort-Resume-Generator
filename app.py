from flask import Flask, render_template, request, make_response
from werkzeug.utils import secure_filename
from weasyprint import HTML
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def home():
    return render_template('form.html')

def process_form_data(request):
    data = request.form.to_dict()

    # Internships
    intern_titles = request.form.getlist("intern_title")
    intern_companies = request.form.getlist("intern_company")
    intern_durations = request.form.getlist("intern_duration")
    intern_descriptions = request.form.getlist("intern_description")
    internships = []
    for i in range(len(intern_titles)):
        if intern_titles[i].strip():
            internships.append({
                "title": intern_titles[i],
                "company": intern_companies[i],
                "duration": intern_durations[i],
                "description": intern_descriptions[i]
            })
    data["internships"] = internships

    # Projects
    titles = request.form.getlist("project_title")
    stacks = request.form.getlist("tech_stack")
    descriptions = request.form.getlist("project_description")
    links = request.form.getlist("project_link")
    projects = []
    for i in range(len(titles)):
        if titles[i].strip():
            projects.append({
                "title": titles[i],
                "tech_stack": stacks[i],
                "description": descriptions[i],
                "link": links[i]
            })
    data["projects"] = projects

    # Achievements
    data["achievements"] = request.form.get("achievements", "").split(";")

    # Photo Upload
    photo = request.files.get("photo")
    if photo and photo.filename != "":
        filename = secure_filename(photo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(filepath)
        data["photo_url"] = "/" + filepath.replace("\\", "/")
        data["photo_path"] = os.path.abspath(filepath)
    else:
        data["photo_url"] = None
        data["photo_path"] = None

    print("PHOTO PATH:", data["photo_path"])  # For debug

    return data

@app.route('/resume', methods=['POST'])
def resume():
    data = process_form_data(request)
    template = request.form.get("template", "template1") + ".html"
    return render_template(template, data=data, pdf=False)

@app.route('/download', methods=['POST'])
def download_pdf():
    data = process_form_data(request)
    template = request.form.get("template", "template1") + ".html"
    html = render_template(template, data=data, pdf=True)

    # FIX: Ensure WeasyPrint can load local file:// paths on Windows
    pdf = HTML(string=html, base_url=os.path.abspath('.')).write_pdf()

    response = make_response(pdf)
    filename = f"{data.get('name', 'resume').replace(' ', '_').lower()}_resume.pdf"
    response.headers["Content-Type"] = "application/pdf"
    response.headers["Content-Disposition"] = f"attachment; filename={filename}"
    return response

if __name__ == '__main__':
    app.run(debug=True)
