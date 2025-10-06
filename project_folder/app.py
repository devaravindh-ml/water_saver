from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_super_secret_key' # Needed for session management

# --- FIX: Make 'enumerate' available to all Jinja templates ---
app.jinja_env.globals.update(enumerate=enumerate)

# --- Quiz Data Structure ---
# Organized by screen/category
QUIZ_DATA = {
    "daily_drip": {
        "title": "Screen 1: The Daily Drip 💧",
        "questions": [
            {
                "q": "How much water do you waste if you leave the tap running for 2 minutes while brushing your teeth?",
                "options": ["About 1 gallon", "About 8 gallons (30 liters)", "About 20 gallons"],
                "answer": "About 8 gallons (30 liters)",
                "fact": "That's enough to compare to the water a small dog drinks in a week! Turn off the tap!"
            },
            {
                "q": "A 10-minute shower with a standard showerhead uses as much water as a bath. (True/False)?",
                "options": ["True", "False"],
                "answer": "True",
                "fact": "A 10-minute shower can use 25–50 gallons, similar to a 36-gallon bath. Shorten those showers!"
            },
            {
                "q": "A leaky faucet dripping one drop per second can waste how much water in one day?",
                "options": ["0.5 gallons", "5-10 gallons", "50 gallons"],
                "answer": "5-10 gallons",
                "fact": "5-10 gallons is enough to fill a laundry basket 5 times! Be a Leak Detective!"
            }
        ],
        "next_route": "virtual_water_voyage",
        "reward": "The 'Toothbrush Hero' Badge 🏅"
    },
    "virtual_water_voyage": {
        "title": "Screen 2: Virtual Water Voyage 👕🍔",
        "questions": [
            {
                "q": "How many gallons of water are used, on average, to produce just ONE cotton T-shirt?",
                "options": ["50 gallons", "300 gallons", "Over 700 gallons"],
                "answer": "Over 700 gallons",
                "fact": "That's enough drinking water for one person for over 3.5 years! Choose sustainable fashion."
            },
            {
                "q": "Which food item has a larger 'water footprint': an apple, a glass of milk, or a hamburger?",
                "options": ["An Apple", "A Glass of Milk", "A Hamburger"],
                "answer": "A Hamburger",
                "fact": "Beef production requires significantly more water than growing plants. Eco-friendly eating matters!"
            },
            {
                "q": "A single sheet of paper requires about 2-13 liters of water to produce. (True/False)?",
                "options": ["True", "False"],
                "answer": "True",
                "fact": "Industrial processes for paper are water-intensive. Think before you print!"
            }
        ],
        "next_route": "eco_action_challenge",
        "reward": "The 'Footprint Investigator' Badge 👣"
    },
    "eco_action_challenge": {
        "title": "Screen 3: Eco-Action Challenge 🌱",
        "questions": [
            {
                "q": "You've just rinsed fruit. What is the most eco-friendly thing to do with that 'greywater'?",
                "options": ["Flush it down the toilet", "Pour it down the sink", "Use it to water a houseplant"],
                "answer": "Use it to water a houseplant",
                "fact": "Simple re-use is a powerful conservation habit. Keep those plants happy!"
            },
            {
                "q": "The 'Navy Shower' technique involves turning the water off for 3 minutes. What are you doing during that time?",
                "options": ["Waiting for the water to heat up", "Soaping up and scrubbing", "Doing a plank"],
                "answer": "Soaping up and scrubbing",
                "fact": "Only use the water to get wet and to rinse—a great water-saving hack!"
            },
            {
                "q": "What does the EPA's WaterSense label on a showerhead primarily mean?",
                "options": ["It's imported", "It's at least 20% more water-efficient", "It has a built-in timer"],
                "answer": "It's at least 20% more water-efficient",
                "fact": "Look for this label to save water without sacrificing shower performance."
            }
        ],
        "next_route": "final_score",
        "reward": "The 'Green Guru' Certificate 🏆"
    }
}

# --- Utility Functions ---

def get_total_questions(category):
    return len(QUIZ_DATA[category]["questions"])

# --- Flask Routes ---

@app.route('/')
def index():
    # Initialize session variables and show the start screen
    session['score'] = 0
    session['completed_quizzes'] = []
    session['rewards'] = []
    return render_template('index.html')

@app.route('/quiz/<category>', methods=['GET', 'POST'])
def quiz_screen(category):
    if category not in QUIZ_DATA:
        return redirect(url_for('index'))

    quiz = QUIZ_DATA[category]
    num_questions = get_total_questions(category)

    if request.method == 'POST':
        user_score = 0
        for i, q_data in enumerate(quiz["questions"]):
            user_answer = request.form.get(f'q{i}')
            if user_answer == q_data["answer"]:
                user_score += 1

        # Update global score and check for reward
        session['score'] += user_score
        session['completed_quizzes'].append(category)

        # Calculate percentage for the current screen
        percentage = int((user_score / num_questions) * 100)
        
        # Determine reward based on performance (e.g., must pass 70%)
        reward_earned = None
        if percentage >= 66:  # 2 out of 3 correct
            reward_earned = quiz["reward"]
            if reward_earned not in session['rewards']:
                session['rewards'].append(reward_earned)

        # Redirect to an intermediate reward/progress screen
        return render_template('results.html', 
                                category=category,
                                score=user_score,
                                total=num_questions,
                                percentage=percentage,
                                reward=reward_earned,
                                next_route=quiz["next_route"])

    # GET request: Display the quiz questions
    return render_template('quiz.html', 
                            quiz=quiz, 
                            category=category)

@app.route('/final_score')
def final_score():
    # Check if all quizzes are done before showing the final screen
    if len(session.get('completed_quizzes', [])) < len(QUIZ_DATA):
        return redirect(url_for('index'))

    total_possible = sum(get_total_questions(cat) for cat in QUIZ_DATA.keys())
    final_percentage = int((session['score'] / total_possible) * 100)
    
    return render_template('final_score.html',
                            final_score=session['score'],
                            total_possible=total_possible,
                            final_percentage=final_percentage,
                            rewards=session.get('rewards', []))

if __name__ == '__main__':
    # Ensure templates directory exists when running
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True)
