# Azure Blob Storage Book Management API

This Flask-based API allows you to manage books stored in Azure Blob Storage. It provides endpoints for performing CRUD operations on books, uploading books from Gutenberg, and searching for words within books.

## Features
- **Book Management:**
  - List all books stored in Azure Blob Storage.
  - Download a specific book by its ID.
  - Delete a book from storage.
  - Add a new book from Gutenberg (via its ID).
  
- **Search Functionality:**
  - Search for a specific word in a book.
  - Search for a word across all books in the container and return the occurrence count.

## Dependencies

### Required Libraries

- **Flask**: For the web framework.
- **Flask-CORS**: For enabling CORS.
- **requests**: To fetch books from Gutenberg.
- **azure-storage-blob**: For interacting with Azure Blob Storage.

You can install all the dependencies using:

```bash
pip install -r requirements.txt
```
**Set your Azure Blob Storage connection string in an environment variable:**

```bash
export AZURE_BLOB_CONNECTION_STRING="your-connection-string-here"
```
**Run the Flask app:**

```bash
python app.py
```
The app will start running on [http://localhost:5000](http://localhost:5000).

## Endpoints

### Book Management

- **GET /raamatud/**  
Retrieves a list of all books stored in the Azure Blob Storage container.

- **GET /raamatud/<book_id>**  
Downloads the content of a specific book by its ID (in .txt format).

- **DELETE /raamatud/<book_id>**  
Deletes a specific book from the Azure Blob Storage container.

- **POST /raamatud/**  
Uploads a new book from Gutenberg based on its ID.

### Search Functionality

- **POST /raamatu_otsing/<raamatu_id>/**  
Searches for a word in a specific book (identified by its ID) and returns the count of occurrences.

- **POST /raamatu_otsing/**  
Searches for a word across all books and returns the count of occurrences for each book.

---

## Docker Usage

To run the project inside a Docker container, Docker must be installed on your machine.

**Build the Docker Image:**  
Navigate to the directory where the Dockerfile is located and run:

```bash
docker build -t azure-book-management .
```

**Run the Docker Container:**  
After building the image, run the following command to start the container:

```bash
docker run
```

This command will start the Flask app inside the Docker container and make it accessible at [http://localhost:5000](http://localhost:5000).

---

**To manage multiple services**
Docker Compose, use the provided docker-compose.yaml file.

```bash
docker-compose up --build
```