# AI Assistant Chatbot using Flask, Neo4j, and Machine Learning
# This file contains the core logic for the chatbot, including
# NLP, Neo4j integration, and Dijkstra's algorithm for navigation.

from flask import Flask, request, jsonify, render_template_string
from neo4j import GraphDatabase
import spacy
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import heapq
import json

# --- Basic Configuration ---
app = Flask(__name__)

# Neo4j Database Connection
# IMPORTANT: Replace with your actual Neo4j credentials
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "12345678"

try:
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    driver.verify_connectivity()
    print("Successfully connected to Neo4j.")
except Exception as e:
    print(f"Failed to connect to Neo4j: {e}")
    # The application will not work without a database connection.
    # In a real-world scenario, you'd handle this more gracefully.
    driver = None

# Load SpaCy model for NLP
try:
    nlp = spacy.load("en_core_web_sm")
except OSError:
    print("Downloading 'en_core_web_sm' model...")
    from spacy.cli import download
    download("en_core_web_sm")
    nlp = spacy.load("en_core_web_sm")

# --- Sample Data and Knowledge Base ---
# In a real application, this would be more extensive or replaced by a proper intent classification model.
knowledge_base = {
    "greeting": ["hello", "hi", "hey", "greetings", "good morning", "good afternoon"],
    "goodbye": ["bye", "goodbye", "see you", "take care"],
    "thanks": ["thanks", "thank you", "appreciate it"],
    "about": ["who are you", "what are you", "what can you do"],
    "navigate": ["navigate", "find", "go to", "reach", "how to get to", "directions"],
    "teacher_info": ["teacher", "faculty", "professor", "details of", "information on", "who is"]
}

# Create a TF-IDF Vectorizer to understand user intent
vectorizer = TfidfVectorizer()
intent_vectors = {intent: vectorizer.fit_transform(phrases) for intent, phrases in knowledge_base.items()}
all_phrases = [phrase for phrases in knowledge_base.values() for phrase in phrases]
vectorizer.fit(all_phrases)

# --- Core Functions ---

def get_intent(user_input):
    """
    Determines the user's intent based on their input using cosine similarity.
    """
    user_vector = vectorizer.transform([user_input.lower()])
    max_similarity = 0
    best_intent = "unknown"

    for intent, phrases in knowledge_base.items():
        for phrase in phrases:
            phrase_vector = vectorizer.transform([phrase])
            similarity = cosine_similarity(user_vector, phrase_vector)[0][0]
            if similarity > max_similarity:
                max_similarity = similarity
                best_intent = intent

    # A threshold to decide if the match is good enough
    if max_similarity > 0.3:
        return best_intent
    return "unknown"


def find_teacher_by_name(tx, first_name):
    """
    Queries the Neo4j database to find teachers by their first name.
    """
    query = (
        "MATCH (t:Teacher) "
        "WHERE toLower(t.firstName) = toLower($first_name) "
        "RETURN t.firstName AS firstName, t.lastName AS lastName, t.phone AS phone, "
        "t.email AS email, t.cabin AS cabin, t.building AS building, t.department AS department"
    )
    result = tx.run(query, first_name=first_name)
    return [record.data() for record in result]


def build_graph_from_neo4j():
    """
    Fetches nodes and relationships from Neo4j to build a graph for Dijkstra's algorithm.
    """
    graph = {}
    with driver.session() as session:
        nodes = session.run("MATCH (n:Location) RETURN n.name AS name").data()
        for node in nodes:
            graph[node['name']] = {}

        rels = session.run("MATCH (a:Location)-[r:CONNECTED_TO]->(b:Location) RETURN a.name AS source, b.name AS target, r.weight AS weight, r.direction AS direction").data()
        for rel in rels:
            if rel['source'] not in graph:
                graph[rel['source']] = {}
            graph[rel['source']][rel['target']] = {'weight': rel['weight'], 'direction': rel['direction']}
    return graph


def dijkstra(graph, start, end):
    """
    Implements Dijkstra's algorithm to find the shortest path.
    """
    queue = [(0, start, [], [])]  # (cost, current_node, path_nodes, path_directions)
    seen = set()
    
    while queue:
        (cost, node, path, directions) = heapq.heappop(queue)
        
        if node not in seen:
            seen.add(node)
            path = path + [node]
            
            if node == end:
                return (cost, path, directions)

            for neighbor, properties in graph.get(node, {}).items():
                if neighbor not in seen:
                    new_cost = cost + properties.get('weight', 1)
                    new_directions = directions + [properties.get('direction', 'move forward')]
                    heapq.heappush(queue, (new_cost, neighbor, path, new_directions))
    return float("inf"), [], []

# --- Chatbot State Management ---
# Simple in-memory state for demonstration. For production, use a database like Redis.
user_sessions = {}

# --- Flask Routes ---

@app.route("/")
def index():
    """

    Serves the main HTML page for the chatbot interface.
    """
    # This renders the HTML from a string. In a larger app, you'd use separate files.
    return render_template_string(open('index.html').read())

@app.route("/chat", methods=['POST'])
def chat():
    """
    The main endpoint for handling user messages.
    """
    data = request.json
    user_id = data.get("user_id", "default_user")
    message = data.get("message", "").strip()

    if user_id not in user_sessions:
        user_sessions[user_id] = {"state": "idle"}
    
    session = user_sessions[user_id]
    
    # --- State-based conversation logic ---
    if session.get("state") == "navigation_confirm":
        if "yes" in message.lower() or "ok" in message.lower() or "reached" in message.lower():
            current_step = session.get("current_step", 0)
            path = session.get("path", [])
            directions = session.get("directions", [])
            
            if current_step < len(path) - 1:
                next_node = path[current_step + 1]
                direction_text = directions[current_step]
                response = f"Great! Now, {direction_text} to reach {next_node}. Let me know when you've reached."
                session["current_step"] += 1
            else:
                response = "You have arrived at your destination!"
                session["state"] = "idle"
        else:
            response = "Okay, I'll wait. Just say 'yes' or 'reached' when you get there."
        return jsonify({"response": response})
        
    if session.get("state") == "teacher_selection":
        try:
            choice = int(message) - 1
            teachers = session.get("teachers", [])
            if 0 <= choice < len(teachers):
                teacher = teachers[choice]
                response = (f"Here are the details for {teacher['firstName']} {teacher['lastName']}:\n"
                            f"Email: {teacher['email']}\n"
                            f"Phone: {teacher['phone']}\n"
                            f"Cabin: {teacher['cabin']} in {teacher['building']}\n"
                            f"Department: {teacher['department']}.\n\n"
                            "Would you like me to navigate you to their cabin?")
                session["state"] = "navigate_to_teacher_confirm"
                session["teacher_cabin"] = teacher['cabin']
            else:
                response = "That's not a valid choice. Please pick a number from the list."
        except ValueError:
            response = "Please enter a number to choose a teacher."
        return jsonify({"response": response})

    if session.get("state") == "navigate_to_teacher_confirm":
        if "yes" in message.lower():
             # Transition to navigation logic
            doc = nlp(f"go from my current location to {session['teacher_cabin']}")
            # This is a simplified way to trigger navigation.
            # Ideally, you'd ask for the user's current location.
            return handle_navigation(doc, user_id)
        else:
            response = "Alright. Let me know if you need anything else!"
            session["state"] = "idle"
        return jsonify({"response": response})

    # --- Intent-based logic ---
    intent = get_intent(message)
    doc = nlp(message)
    
    if intent == "greeting":
        response = "Hello! How can I help you today? You can ask me for directions or information about teachers."
    elif intent == "goodbye":
        response = "Goodbye! Have a great day."
    elif intent == "thanks":
        response = "You're welcome!"
    elif intent == "about":
        response = "I am a friendly AI assistant. I can help you navigate the campus and find information about faculty members."
    elif intent == "navigate":
        return handle_navigation(doc, user_id)
    elif intent == "teacher_info":
        names = [ent.text for ent in doc.ents if ent.label_ == "PERSON"]
        if names:
            first_name = names[0].split()[0] # Use the first name
            with driver.session() as dbsession:
                teachers = dbsession.execute_read(find_teacher_by_name, first_name)
            
            if not teachers:
                response = f"I couldn't find any teacher named {first_name}."
            elif len(teachers) == 1:
                teacher = teachers[0]
                response = (f"Here are the details for {teacher['firstName']} {teacher['lastName']}:\n"
                            f"Email: {teacher['email']}\n"
                            f"Phone: {teacher['phone']}\n"
                            f"Cabin: {teacher['cabin']} in {teacher['building']}\n"
                            f"Department: {teacher['department']}.\n\n"
                            "Would you like me to navigate you to their cabin?")
                session["state"] = "navigate_to_teacher_confirm"
                session["teacher_cabin"] = teacher['cabin']

            else:
                response = "I found multiple teachers with that name. Please choose one:\n"
                for i, t in enumerate(teachers):
                    response += f"{i+1}. {t['firstName']} {t['lastName']} ({t['department']})\n"
                session["state"] = "teacher_selection"
                session["teachers"] = teachers
        else:
            response = "I can help with teacher details. Who are you looking for?"
    else:
        response = "I'm not sure how to help with that. You can ask me for directions like 'navigate from ab1 303 to ab2 112' or 'who is [teacher's name]?'"
        
    return jsonify({"response": response})


def handle_navigation(doc, user_id):
    """
    Handles the logic for navigation requests.
    """
    locations = [ent.text.upper() for ent in doc.ents if ent.label_ in ("GPE", "LOC", "ORG", "FAC")]
    # A simple way to extract start and end points. Might need refinement.
    # Look for keywords like 'from' and 'to'.
    text_tokens = [token.text for token in doc]
    start_node, end_node = None, None
    try:
        if 'from' in text_tokens and 'to' in text_tokens:
            from_index = text_tokens.index('from')
            to_index = text_tokens.index('to')
            start_node = text_tokens[from_index + 1].upper()
            end_node = text_tokens[to_index + 1].upper()
        elif len(locations) >= 2:
            start_node = locations[0]
            end_node = locations[1]
    except IndexError:
        pass

    if start_node and end_node:
        campus_graph = build_graph_from_neo4j()
        
        # Check if nodes exist
        if start_node not in campus_graph or end_node not in campus_graph:
            return jsonify({"response": f"Sorry, I don't recognize one of the locations: {start_node} or {end_node}. Please use known location names."})

        cost, path, directions = dijkstra(campus_graph, start_node, end_node)
        
        if path:
            session = user_sessions[user_id]
            session["state"] = "navigation_confirm"
            session["path"] = path
            session["directions"] = directions
            session["current_step"] = 0
            
            first_direction = directions[0]
            first_destination = path[1]
            response = f"Okay, starting navigation from {start_node} to {end_node}. First, {first_direction} to reach {first_destination}. Let me know when you're there."
        else:
            response = f"I'm sorry, I couldn't find a path from {start_node} to {end_node}."
    else:
        response = "I can help with navigation. Please tell me where you are starting from and where you want to go, for example: 'Navigate from AB1-101 to AB2-205'."
        
    return jsonify({"response": response})


@app.route("/setup-data", methods=['GET'])
def setup_data():
    """
    A helper endpoint to populate Neo4j with sample data.
    THIS SHOULD BE REMOVED OR SECURED IN A PRODUCTION ENVIRONMENT.
    """
    if not driver:
        return "Neo4j driver not available.", 500

    with driver.session() as session:
        # Clear existing data
        session.run("MATCH (n) DETACH DELETE n")
        
        # Create Locations
        locations = [
            "AB1_ENTRANCE", "AB1_303", "AB1_310", "AB1_LIFT", "AB1_STAIRS", "AB1_EXIT",
            "CROSSROAD_1", "CANTEEN", "LIBRARY_ENTRANCE", "AB2_ENTRANCE", "AB2_112",
            "AB2_LIFT", "AB2_EXIT", "PARKING_LOT"
        ]
        for loc in locations:
            session.run("CREATE (:Location {name: $name})", name=loc)
            
        # Create Connections
        connections = [
            ("AB1_ENTRANCE", "AB1_303", 10, "go straight down the corridor"),
            ("AB1_303", "AB1_310", 5, "continue straight"),
            ("AB1_310", "AB1_LIFT", 8, "turn left towards the lift"),
            ("AB1_310", "AB1_STAIRS", 8, "turn right for the stairs"),
            ("AB1_LIFT", "AB1_EXIT", 12, "exit the building from the main door"),
            ("AB1_STAIRS", "AB1_EXIT", 12, "exit the building from the main door"),
            ("AB1_EXIT", "CROSSROAD_1", 20, "walk across the lawn"),
            ("CROSSROAD_1", "CANTEEN", 15, "take the path on your left"),
            ("CROSSROAD_1", "LIBRARY_ENTRANCE", 15, "take the path on your right"),
            ("CROSSROAD_1", "AB2_ENTRANCE", 25, "walk straight ahead towards the next building"),
            ("AB2_ENTRANCE", "AB2_LIFT", 10, "enter and find the lift on your right"),
            ("AB2_ENTRANCE", "AB2_112", 15, "go straight and take the first right"),
            ("AB2_LIFT", "AB2_112", 5, "exit the lift and turn left"),
            ("AB2_EXIT", "PARKING_LOT", 30, "follow the main path out")
        ]
        
        for start, end, weight, direction in connections:
            # Create relationships in both directions
            session.run("""
                MATCH (a:Location {name: $start}), (b:Location {name: $end})
                CREATE (a)-[:CONNECTED_TO {weight: $weight, direction: $direction}]->(b)
            """, start=start, end=end, weight=weight, direction=direction)
            # For simplicity, reverse directions are generic. Can be improved.
            session.run("""
                MATCH (a:Location {name: $start}), (b:Location {name: $end})
                CREATE (b)-[:CONNECTED_TO {weight: $weight, direction: 'go back towards ' + $start}]->(a)
            """, start=start, end=end, weight=weight)

        # Create Teachers
        teachers = [
            {'firstName': 'Aayush', 'lastName': 'Sharma', 'phone': '9876543210', 'email': 'Aayush.sharma@university.edu', 'cabin': 'AB1_303', 'building': 'AB1', 'department': 'Computer Science'},
            {'firstName': 'Sneha', 'lastName': 'Verma', 'phone': '8765432109', 'email': 'sneha.verma@university.edu', 'cabin': 'AB2_112', 'building': 'AB2', 'department': 'Electronics'},
            {'firstName': 'Aarav', 'lastName': 'Gupta', 'phone': '7654321098', 'email': 'aarav.gupta@university.edu', 'cabin': 'AB2_112', 'building': 'AB2', 'department': 'Mechanical'}
        ]
        
        for t in teachers:
            session.run("""
                CREATE (p:Teacher {
                    firstName: $firstName, 
                    lastName: $lastName, 
                    phone: $phone, 
                    email: $email, 
                    cabin: $cabin, 
                    building: $building, 
                    department: $department
                })
                WITH p
                MATCH (l:Location {name: $cabin})
                CREATE (p)-[:HAS_CABIN_AT]->(l)
            """, **t)

        return "Sample data has been successfully loaded into Neo4j.", 200

if __name__ == '__main__':
    app.run(debug=True, port=5000)
