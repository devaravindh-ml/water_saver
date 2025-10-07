from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'your_super_secret_key'  # Needed for session management

# --- Make 'enumerate' available in Jinja templates ---
app.jinja_env.globals.update(enumerate=enumerate)

# --- Quiz Data Structure ---
QUIZ_DATA = {
    "daily_drip": {
        "title": "Screen 1: The Daily Drip 💧",
        "questions": [
            {
                "q": "If you leave the tap open for 2 minutes while brushing, how much water is wasted?",
                "options": ["About 4 liters", "About 30 liters", "About 75 liters"],
                "answer": "About 30 liters",
                "fact": "That is like the water a small dog drinks in one week! Close the tap!"
            },
            {
                "q": "Does a 10-minute shower use the same water as filling a bucket and washing? (Yes or No)",
                "options": ["Yes", "No"],
                "answer": "Yes",
                "fact": "A 10-minute shower can use 90 to 190 liters of water, like a big bucket. Try to take short showers!"
            },
            {
                "q": "A tap that drips one drop every second wastes how much water in one day?",
                "options": ["2 liters", "20–40 liters", "190 liters"],
                "answer": "20–40 liters",
                "fact": "This is enough water to fill a big basket 5 times! Fix leaking taps!"
            }
        ],
        "next_route": "virtual_water_voyage",
        "reward": "The 'Toothbrush Hero' Badge 🏅"
    },

    "virtual_water_voyage": {
        "title": "Screen 2: Virtual Water Voyage 👕🍔",
        "questions": [
            {
                "q": "How much water is used to make one cotton T-shirt?",
                "options": ["190 liters", "1,100 liters", "Over 2,600 liters"],
                "answer": "Over 2,600 liters",
                "fact": "That is enough drinking water for one person for over 3 years! Choose clothes wisely."
            },
            {
                "q": "Which uses more water: an apple, a glass of milk, or a hamburger?",
                "options": ["Apple", "Glass of milk", "Hamburger"],
                "answer": "Hamburger",
                "fact": "Meat needs much more water than plants. Eating less meat saves water!"
            },
            {
                "q": "Making one sheet of paper needs a lot of water. (True or False)",
                "options": ["True", "False"],
                "answer": "True",
                "fact": "One paper sheet needs 2 to 13 liters to make. Use paper carefully!"
            }
        ],
        "next_route": "eco_action_challenge",
        "reward": "The 'Footprint Investigator' Badge 👣"
    },

    "eco_action_challenge": {
        "title": "Screen 3: Eco-Action Challenge 🌱",
        "questions": [
            {
                "q": "You washed fruit and have leftover water. What is best to do with it?",
                "options": ["Flush it in toilet", "Pour down sink", "Water a plant"],
                "answer": "Water a plant",
                "fact": "Using leftover water for plants saves water. Plants like it!"
            },
            {
                "q": "When you take a 'Navy Shower', you turn off water for 3 minutes. What do you do then?",
                "options": ["Wait for hot water", "Use soap and clean", "Do exercise"],
                "answer": "Use soap and clean",
                "fact": "Turn off water when soaping to save water!"
            },
            {
                "q": "If a showerhead has a WaterSense label, what does it mean?",
                "options": ["It is imported", "It saves 20% or more water", "It has a timer"],
                "answer": "It saves 20% or more water",
                "fact": "WaterSense showerheads save water but still work well."
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
        submitted_answers = {}
        for i, q_data in enumerate(quiz["questions"]):
            user_answer = request.form.get(f'q{i}')
            submitted_answers[f'q{i}'] = user_answer
            if user_answer == q_data["answer"]:
                user_score += 1

        # Update global score and completed quizzes list
        session['score'] += user_score
        if category not in session.get('completed_quizzes', []):
            session['completed_quizzes'].append(category)

        percentage = int((user_score / num_questions) * 100)

        reward_earned = None
        if percentage >= 66:
            reward_earned = quiz["reward"]
            if reward_earned not in session.get('rewards', []):
                session['rewards'].append(reward_earned)

        # Pass submitted answers and correct answers to the template
        return render_template('quiz.html',
                               quiz=quiz,
                               category=category,
                               submitted_answers=submitted_answers,
                               correct_answers=[q["answer"] for q in quiz["questions"]],
                               reward=reward_earned,
                               show_results=True)  # flag to show answers

    # GET request: show quiz normally
    return render_template('quiz.html',
                           quiz=quiz,
                           category=category,
                           submitted_answers=None,
                           correct_answers=None,
                           show_results=False)

@app.route('/final_score')
def final_score():
    if len(session.get('completed_quizzes', [])) < len(QUIZ_DATA):
        return redirect(url_for('index'))

    total_possible = sum(get_total_questions(cat) for cat in QUIZ_DATA.keys())
    final_percentage = int((session['score'] / total_possible) * 100)

    return render_template('final_score.html',
                           final_score=session['score'],
                           total_possible=total_possible,
                           final_percentage=final_percentage,
                           rewards=session.get('rewards', []))

# ✅ New route added for login redirect
@app.route('/index')
def go_to_index():
    return render_template('index.html')

@app.route('/')
def login_page():
    return render_template('login.html')

@app.route('/index')
def index():
    session['score'] = 0
    session['completed_quizzes'] = []
    session['rewards'] = []
    return render_template('index.html')



# --- Run the App ---
if __name__ == '__main__':
    import os
    if not os.path.exists('templates'):
        os.makedirs('templates')
    app.run(debug=True, port=5033)
