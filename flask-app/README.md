# Flask Application

This project is a Flask web application structured to facilitate development and testing. Below is an overview of the project components and how to set it up.

## Project Structure

```
flask-app
├── src
│   ├── app
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes.py
│   │   └── config.py
│   └── wsgi.py
├── tests
│   └── test_app.py
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd flask-app
   ```

2. Build the Docker image:
   ```
   docker build -t flask-app .
   ```

3. Run the application:
   ```
   docker run -p 8000:8000 flask-app
   ```

### Running with Docker Compose

If you have a `docker-compose.yml` file set up for multi-container support (e.g., with a database), you can start the application using:

```
docker-compose up
```

### Application Structure

- **src/app/__init__.py**: Initializes the Flask application and loads configurations.
- **src/app/main.py**: Entry point for the application, starts the Flask server.
- **src/app/routes.py**: Defines the routing for the application, handling requests to various endpoints.
- **src/app/config.py**: Manages application settings and environment variables.
- **src/wsgi.py**: WSGI entry point for serving the Flask application.
- **tests/test_app.py**: Contains unit and integration tests for the application.

### Dockerfile

The Dockerfile is configured to use Python 3.12.7 and sets up the environment for running the Flask application with Gunicorn.

### Notes

- If your application requires additional services (like a database), consider using Docker Compose for a multi-container setup.
- Ensure that all dependencies are listed in `requirements.txt` for proper installation.

## License

This project is licensed under the MIT License - see the LICENSE file for details.