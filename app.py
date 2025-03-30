from flask import Flask, request, render_template, Markup
import os
import google.generativeai as genai
import textwrap

app = Flask(__name__)

def setup_gemini_api():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("Please set the GEMINI_API_KEY environment variable.")
    genai.configure(api_key=api_key)
    return genai.GenerativeModel('gemini-1.5-flash')

def generate_itinerary_with_gemini(user_inputs, model):
    destination = user_inputs["destination"]
    days = user_inputs["days"]
    budget = user_inputs["budget"]
    cuisine_preference = user_inputs["cuisine_preference"]
    people_number = user_inputs["people_number"]
    interests = user_inputs["interests"]
    budget_per_day = budget / days / people_number
    prompt = (
        f"Generate a visually appealing and easy-to-read {days}-day travel itinerary for {destination}. "
        f"The budget is ${budget} for {people_number} people, so approximately ${budget_per_day:.2f} per person per day. "
        f"The user prefers {cuisine_preference or 'no specific'} cuisine and is interested in {interests}. "
        f"Present the itinerary in a structured format, with clear headings for each day. "
        f"Use bullet points or numbered lists for activities and dining recommendations. "
        f"Include estimated times for each activity and brief descriptions. For each day, provide total estimated cost. "
        f"Format the itinerary as:\n"
        f"**Day 1:**\n"
        f"- Morning (9:00 AM - 12:00 PM): [Activity] - [Brief description] - [Estimated cost]\n"
        f"- Lunch (12:00 PM - 1:00 PM): [Dining recommendation] - [Estimated cost]\n"
        f"- Afternoon (1:00 PM - 5:00 PM): [Activity] - [Brief description] - [Estimated cost]\n"
        f"- Evening (7:00 PM onwards): [Activity/Dinner] - [Estimated cost]\n"
        f"**Total Estimated Day 1 Cost:** [Total Cost]\n\n"
        f"**Day 2:**\n"
        f"... and so on for each day."
    )
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"An error occurred during API call: {e}"

@app.route('/', methods=['GET', 'POST'])
def itinerary_generator():
    if request.method == 'POST':
        user_inputs = {
            "origin": request.form['origin'],
            "destination": request.form['destination'],
            "days": int(request.form['days']),
            "budget": float(request.form['budget']),
            "cuisine_preference": request.form['cuisine_preference'],
            "people_number": int(request.form['people_number']),
            "interests": request.form['interests'],
        }
        model = setup_gemini_api()
        itinerary = generate_itinerary_with_gemini(user_inputs, model)
        return render_template('index.html', itinerary=Markup(itinerary.replace('\n', '<br>')))
    return render_template('index.html', itinerary=None)

if __name__ == '__main__':
    # Remove debug=True for production
    app.run(debug=True)
    pass #gunicorn will run the app.
