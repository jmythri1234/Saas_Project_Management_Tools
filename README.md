🚀 ProjectFlow – SaaS Project Management Tool

A web-based project management application built with Python Flask to organize projects, manage tasks, track deadlines, and monitor project progress through a dashboard.

✨ Features

- 🔐 User Registration and Login
- 📊 Interactive Dashboard with Project Statistics
- 📁 Create, View, and Manage Projects
- ✅ Task Management with Priorities and Deadlines
- 🔄 Update Task Status and Track Completion
- 📈 Project Progress Tracking
- 👥 Team Page
- 🗄️ SQLite Database Integration

🛠️ Tech Stack

- Backend: Python, Flask
- Frontend: HTML, CSS
- Database: SQLite
- Authentication: Flask-Login
- ORM: Flask-SQLAlchemy

📂 Project Structure

SaaS_Project_Management_Tool/
├── app.py
├── requirements.txt
├── .gitignore
├── instance/
├── static/
│   ├── css/
│   ├── js/
│   └── images/
├── templates/
│   ├── index.html
│   ├── register.html
│   ├── login.html
│   ├── dashboard.html
│   ├── projects.html
│   ├── project_details.html
│   ├── tasks.html
│   ├── team.html
│   └── base.html
├── screenshots/
└── README.md

⚙️ Installation and Setup

1. Clone the repository:
   
   git clone https://github.com/jmythri1234/Saas_Project_Management_Tools.git

2. Open the project folder:
   
   cd SaaS_Project_Management_Tools

3. Create a virtual environment:
   
   python -m venv venv

4. Activate the virtual environment on Windows:
   
   venv\Scripts\activate

5. Install dependencies:
   
   pip install -r requirements.txt

6. Run the application:
   
   python app.py

7. Open the local URL displayed in the terminal, usually:
   
   "http://127.0.0.1:5000"

📸 Screenshots

🏠 Home Page

"Home Page" (Screenshots/home.png)

📊 Dashboard

"Dashboard" (Screenshots/dashboard.png)

📁 Projects

"Projects" (Screenshots/projects.png)

✅ Tasks

"Tasks" (Screenshots/tasks.png)

📋 Project Details

"Project Details" (Screenshots/project_details.png)

🔐 Login

"Login" (Screenshots/login.png)

📝 Registration

"Registration" (Screenshots/register.png)

🔒 Security Notes

- Do not upload passwords, API keys, secret keys, or ".env" files.
- Keep virtual environments and local database files out of GitHub.
- Configure a secure secret key before deploying publicly.

🚀 Future Enhancements

- Team Member Management
- Email Notifications and Reminders
- Advanced Reports and Analytics
- Cloud Deployment

👨‍💻 Author

Jikkappagari Mythri

🔗 GitHub: "@jmythri1234" (https://github.com/jmythri1234)

---

⭐ If you find this project useful, consider giving the repository a star!
