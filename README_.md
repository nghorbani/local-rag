I want to make a ARG system based based on flast and pgvector.
it has three components: extracting text from jpeg images, storingn text in md files, running embeding model to convert text and USE HMNB to search for relevant text.
it enables chatting with the fetched text too.
it has a venv file to store ocr model name and url, embedding model name and url, chat model name and url, and pgvector connection details.
it also holds flast app details like host and port.
it will also get the document root directory to store the md files.

the flast app has a home page that shows list of all the documents detected. it holds rel_path to the images and the md files.
if shows how many files has been detected, how many has been ocrd, how many has been embedded. if one clicks on a row, which is a document, it shows the images and the md files side by side. while the image 
is interactible i.e. onecan zoom in and pan in the overlayed screen. the md file is shown in a read only mode. there is a button to run ocr on the image and store the text in the md file. there is another button to run embedding model on the text and store the vector in pgvector.
there a button to process al the files that has not been ocrd or embedded.
there is a tab to search among the embeded text, user gives some text that could be in the document and the tool lists the relevant documents based on the similarity score. one can click on a document to see the images and the md file side by side. 
one can also run the chat model to chat with the document. the chat model uses the embedding to fetch relevant text and uses that as context to chat with the user. 
use ollama-ocr with qwen2.5vl:3b at http://localhost:11434 for embedding use snowflake-arctic-embed2:latest and for chat use openapi-sdk with ollama local deepseek-r1:1.5b.
the ollama is being accesssed through a tunel hence you cannot call ollama diretly. you have to use the url http://localhost:11434/v1/chat/completions for chat and http://localhost:11434/v1/embeddings for embedding. assume models already pulled
use uv for managign python environment. use ruff for linting. use pytest for testing. 

decompose this into a series of tasks and subtasks with a title and description for each task and subtask. at the end of each task there shoudl be a pytest scenario to test the task.
the test image is avaible under root assets/sample.jpg. 
