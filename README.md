
# Project Claiming Website

This project aims to create a web application where professors can list their available projects, and students can claim these projects for their academic endeavors.

## Features

- **User Authentication**: Users can register, log in, and log out of the system. Professors and students have separate registration forms.

- **Professor Dashboard**: Professors can view, create, update, and delete their projects. They can also view a list of students who have claimed their projects.

- **Student Dashboard**: Students can view a list of available projects, claim a project, and view the projects they have claimed.

## Technologies Used

- **Django**: Django is used as the backend framework to handle server-side logic, user authentication, and database management.

- **Django REST Framework**: Django REST Framework is used to create RESTful APIs for communication between the frontend and backend.

- **SQLite**: SQLite is used as the default database to store project, professor, and student data.

- **HTML/CSS/JavaScript**: Frontend components are built using HTML, CSS, and JavaScript to provide a user-friendly interface.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/meytiii/Project-claiming-website
2.  Navigate to the project directory:
    ```bash
    cd project-claiming-website
3.  Install dependencies:
    ```bash
    pip install -r requirements.txt
4.  Run database migrations:
    ```bash
    python manage.py migrate
5.  Start the development server:
    ```bash
    python manage.py runserver
6.  Access the application in your web browser at [http://localhost:8000](http://localhost:8000/).
    

## Usage

1.  Register as a professor or student using the provided registration forms.
    
2.  Log in with your credentials.
    
3.  Professors can create projects and manage their availability.
    
4.  Students can view available projects and claim them for their academic work.
    

## Contributing

Contributions are welcome! Please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License.

Feel free to customize this README.md file further to match any additional features or specifications of your project! Let me know if you need any further assistance.

