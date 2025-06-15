# Swadsutra Food 🍽️

An AI-powered food recognition and recipe recommendation system that helps users identify food items from images and get instant recipe suggestions.

## 🌟 Features

- **Food Recognition**: Upload food images and get instant identification
- **Recipe Suggestions**: Get detailed recipes for recognized food items
- **User Authentication**: Secure login and registration system
- **Email Verification**: Two-step verification process
- **Responsive Design**: Works on all devices
- **Secure File Handling**: Safe image upload and processing

## 🛠️ Technologies Used

### Backend
- Flask (Python web framework)
- SQLite (Database)
- TensorFlow (AI/ML framework)
- ResNet50 (Pre-trained model for image classification)

### Frontend
- HTML5
- CSS3
- JavaScript
- Bootstrap (for responsive design)

### Tools & Services
- Docker (Containerization)
- Gunicorn (WSGI HTTP Server)
- Git (Version Control)
- SMTP (Email Service)

## 📋 Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment (recommended)
- Git

## 🚀 Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/swadsutra-food.git
cd swadsutra-food
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
# Create .env file
SECRET_KEY=your_secret_key
SMTP_USERNAME=your_email@gmail.com
SMTP_PASSWORD=your_app_password
DATABASE_URL=sqlite:///users.db
BASE_URL=http://127.0.0.1:5000
```

5. Initialize the database:
```bash
python init_db.py
```

## 💻 Usage

1. Start the Flask server:
```bash
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Register a new account or login
4. Upload food images
5. Get instant recognition and recipe suggestions

## 🔒 Security Features

- Password hashing using Werkzeug
- Email verification system
- Secure file upload handling
- Session management
- Environment variable protection
- SQL injection prevention

## 📁 Project Structure

```
swadsutra-food/
├── app.py                 # Main application file
├── requirements.txt       # Project dependencies
├── .env                  # Environment variables
├── static/              # Static files
│   ├── uploads/        # Uploaded images
│   └── css/           # Stylesheets
├── templates/          # HTML templates
├── model/             # AI model files
│   ├── food_classifier_resnet50.h5
│   └── class.txt
└── dataset/           # Recipe dataset
    └── recipe_model.csv
```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Prem Prajapati** [22IT127]
- **Harsh Rohit** [22IT132]

## 🙏 Acknowledgments

- Kundaben Dinsha Patel Institute of Technology
- TensorFlow team for ResNet50 model
- Flask community for excellent documentation

## 📞 Contact

For any queries or support, please contact:
- Prem Prajapati: [premprajapati6514@gmail.com]
- Harsh Rohit: [rohitharsh050@gmail.com]

## 🔄 Future Enhancements

- Nutrition analysis
- Community recipe sharing
- Mobile app integration
- Multi-language support
- Advanced analytics
- Real-time chat support 
