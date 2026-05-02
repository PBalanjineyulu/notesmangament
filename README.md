# 📝 Notes App (Flask)

A simple and secure **Notes Management Web Application** built using **Flask, MySQL, and Bootstrap**.  
This application allows users to create, update, delete, and manage notes efficiently with file upload support and email-based authentication.

---

## 🚀 Features

- 🔐 User Registration & Login  
- 📧 Email OTP Verification (Flask-Mail)  
- 🔑 Forgot Password using OTP  
- 📝 Create, Edit, Delete Notes  
- 📎 Upload Attachments (PDF, files)  
- 🔍 Search Notes  
- 🕒 Track Last Updated Time & User  
- 📱 Fully Responsive UI (Mobile Friendly)  

---

## 🛠️ Tech Stack

- **Backend:** Flask (Python)  
- **Database:** MySQL  
- **Frontend:** HTML, CSS, Bootstrap  
- **Email Service:** Flask-Mail (Gmail SMTP)  

---

## 📂 Project Structure

```
notes-app/
│
├── templates/          
├── app.py              
├── config_example.py   
├── requirements.txt    
├── .gitignore          
└── README.md           
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository

```
git clone https://github.com/YOUR_USERNAME/notes-app.git
cd notes-app
```

---

### 2️⃣ Create Virtual Environment

```
python -m venv venv
venv\Scripts\activate
```

---

### 3️⃣ Install Dependencies

```
pip install -r requirements.txt
```

---

### 4️⃣ Setup Configuration

Create a file named **config.py**

Copy from:

```
config_example.py → config.py
```

Update the values:

```
SECRET_KEY = "your_secret_key"

MAIL_USERNAME = "your_email@gmail.com"
MAIL_PASSWORD = "your_gmail_app_password"

DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = "your_db_password"
DB_NAME = "notesapp"
```

---

### 5️⃣ Run the Application

```
python app.py
```

Open in browser:

```
http://127.0.0.1:5000
```

---

## 🔐 Security Note

- Do NOT upload `config.py` to GitHub  
- Use `.gitignore` to protect sensitive files  
- Always use Gmail App Password  

---

## 📸 Screenshots

(Add your screenshots here)

---

## 👨‍💻 Author

**Your Name**  
GitHub: https://github.com/YOUR_USERNAME  

---

## ⭐ Support

If you like this project, please give it a ⭐ on GitHub!
