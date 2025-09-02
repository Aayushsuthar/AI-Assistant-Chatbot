# AI-Assistant-Chatbot
Campus AI Assistant Chatbot
Welcome to the Campus AI Assistant Chatbot, a smart, conversational guide designed to revolutionize the campus experience. This project provides a sophisticated and friendly chatbot that serves as a personal assistant for students, faculty, and visitors. Whether you're trying to find your way to a lecture hall, looking for a professor's office, or just have a quick question, this chatbot has you covered.

Built on a powerful tech stack, it leverages Python and Flask for a robust backend, spaCy for cutting-edge Natural Language Processing (NLP), and a Neo4j graph database to intelligently map out and understand the complex relationships of a campus environment. This allows for highly efficient pathfinding and data retrieval, making campus life simpler and more connected.

📖 Table of Contents
Features

How It Works

Tech Stack

Getting Started

Usage Examples

Project Structure

Contributing

License

✨ Features
Natural Language Processing: The chatbot fluently understands formal English, informal English, and Hinglish, making it accessible to a diverse user base.

Friendly & Conversational: It's designed to be more than just a tool. It interacts with users in a helpful, friendly tone, creating an engaging user experience.

Turn-by-Turn Navigation: Utilizes Dijkstra's algorithm on the Neo4j graph to find the shortest path between any two locations. It delivers directions step-by-step, waiting for user confirmation ("yes", "ok", "reached") before providing the next instruction.

Intelligent Faculty Search: Users can find faculty members by providing just a first name. The system handles ambiguity by presenting a list of choices if multiple faculty members share the same name, ensuring the user finds the right person.

Graph-Powered Knowledge Base: The entire campus layout—buildings, rooms, pathways, and faculty offices—is modeled as a graph in Neo4j. This provides a flexible and powerful way to query complex spatial and relational data.

Machine Learning for Intent Classification: A pre-trained Scikit-learn model accurately predicts the user's intent (e.g., greet, Maps, find_teacher), allowing the chatbot to trigger the correct logic and provide relevant responses.

🧠 How It Works
The chatbot processes user requests through a simple yet powerful pipeline:

User Input: The user sends a message through the web interface.

Intent Classification: The Flask backend receives the message. The trained Scikit-learn model analyzes the text to classify the user's primary goal (e.g., asking for directions).

Entity Extraction: Using spaCy, the system identifies key pieces of information (entities) from the message, such as location names ("AB1 303") or teacher names ("John").

Graph Database Query: Based on the intent and entities, the application constructs a Cypher query to retrieve information from the Neo4j database. For navigation, this involves running the Dijkstra pathfinding algorithm.

Response Generation: The query results are processed and formatted into a user-friendly, natural language response.

State Management: For multi-turn conversations like navigation, the chatbot maintains the user's state (e.g., current location, destination, path progress) to provide contextual follow-up instructions.

🛠️ Tech Stack
Backend: Python with Flask for creating the web server and API endpoints.

Database: Neo4j Graph Database for storing and querying campus layout and relationship data.

NLP: spaCy for tokenization, lemmatization, and named entity recognition.

Machine Learning: Scikit-learn for training and deploying the intent classification model.

Frontend: Simple HTML, CSS, and JavaScript for the user-facing chat interface.

🚀 Getting Started
Follow these instructions to get the project up and running on your local machine.

Prerequisites
Python (3.8 or newer)

Neo4j Desktop

A code editor like Visual Studio Code

Installation & Setup
Clone the Repository:

git clone [https://github.com/your-username/your-repo-name.git](https://github.com/your-username/your-repo-name.git)
cd your-repo-name

Set Up the Neo4j Database:

Open Neo4j Desktop and create a new local database instance.

Set a memorable password (e.g., password).

Start the database (it should be green and running).

Create a Python Virtual Environment:

python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate  # On Windows

Install Dependencies:

pip install flask neo4j spacy scikit-learn
python -m spacy download en_core_web_sm

Configure the Application:

Open the chatbot_app.py file.

Update the NEO4J_PASSWORD variable with the password you set for your database.

# Ensure this matches the password from Step 2
NEO4J_PASSWORD = "your_neo4j_password"

Running the Application
Start the Flask Server:

python chatbot_app.py

The terminal will confirm a successful connection to Neo4j and show that the server is running on http://127.0.0.1:5000.

Load the Graph Data (One-Time Step):

Open your web browser and go to: http://127.0.0.1:5000/setup-data

A success message will appear once the data is loaded into Neo4j.

Launch the Chatbot:

Navigate to the main page: http://127.0.0.1:5000/

You can now start chatting!

💬 Usage Examples
Greeting:

You: Hello there

Bot: Hello! How can I help you today?

Finding a Teacher:

You: Find professor John

Bot: I found multiple teachers with that name. Please choose one: John Doe (Engineering), John Smith (Arts).

Navigation:

You: I am at ab1 303 and want to reach ab2 112

Bot: Okay, starting navigation. First, go straight until you reach ab1 310. Have you reached?

You: yes

Bot: Great! Now, take a left and walk towards the main exit of AB1...

📂 Project Structure
.
├── chatbot_app.py      # Main Flask application, NLP logic, and database connections.
├── index.html          # The frontend user interface for the chatbot.
└── README.md           # This documentation file.

Step-by-Step Guide: Running the Chatbot in VS Code
This guide will walk you through setting up and running the AI Chatbot project using Visual Studio Code.

Step 1: Prerequisites
Before you begin, make sure you have the following installed:

Visual Studio Code: Download it from the official website.

Python: Install Python 3.8 or newer from python.org. Make sure to check the box that says "Add Python to PATH" during installation.

Python Extension for VS Code: Open VS Code, go to the Extensions view (Ctrl+Shift+X), and install the official Python extension by Microsoft.

Neo4j Desktop: Download and install Neo4j Desktop from the Neo4j website. This is the easiest way to run a local graph database.
https://neo4j.com/download/

Step 2: Set Up Your Project Folder
Create a new folder on your computer (e.g., ai-chatbot).

Place the chatbot_app.py and index.html files inside this folder.

Open VS Code, and then open this folder by going to File > Open Folder....

Step 3: Set Up the Neo4j Database
Open Neo4j Desktop.

Create a new project.

Inside the project, create a new Local DBMS.

Set a password for the database. Remember this password! For example, password.

Click the Start button to run the database. It should turn green when it's active.

Step 4: Configure the Python Environment in VS Code
Open the Terminal: In VS Code, open the integrated terminal by pressing Ctrl+`  (backtick) or going to View > Terminal.

Create a Virtual Environment: It's a best practice to keep project dependencies separate. Run this command in the terminal:

python -m venv .venv

Activate the Virtual Environment:

On Windows:

.venv\Scripts\activate

On macOS/Linux:

source .venv/bin/activate

Your terminal prompt should now show (.venv) at the beginning.

Select the Interpreter: Press Ctrl+Shift+P to open the Command Palette, type "Python: Select Interpreter", and choose the one that has (.venv) in its path.

Step 5: Install Required Libraries
With your virtual environment active in the VS Code terminal, run the following command to install the necessary Python packages:

pip install flask neo4j spacy scikit-learn

Next, download the language model for spaCy:

python -m spacy download en_core_web_sm

Step 6: Update the Application Configuration
In the VS Code editor, open the chatbot_app.py file.

Find the Neo4j connection details near the top of the file.

Change the NEO4J_PASSWORD to the password you set up in Neo4j Desktop in Step 3.

# ...
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "password" # <-- CHANGE THIS
# ...

Save the file.

Step 7: Run the Chatbot and Load the Data
Start the Backend Server: In the VS Code terminal (with the .venv activated), run the main Python file:

python chatbot_app.py

You should see output confirming the Flask server is running and has successfully connected to Neo4j.

Load the Sample Data: Open a web browser (like Chrome or Firefox) and navigate to the following URL. This will populate your database with the dataset from the Python file.
https://www.google.com/url?sa=E&source=gmail&q=http://127.0.0.1:5000/setup-data
You only need to do this step once.

Launch the Chatbot: Finally, go to the main application URL in your browser:
http://127.0.0.1:5000/

You should now see the chat interface and can begin testing your AI assistant!

🤝 Contributing
Contributions, issues, and feature requests are welcome! Feel free to check the issues page for this repository. Please adhere to this project's code of conduct.

📄 License
This project is licensed under the MIT License - see the LICENSE.md file for details.
