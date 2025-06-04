import streamlit as st
import pandas as pd
import random
from Util import QuestionGenerator
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


# handle quiz functionality
class QuizManager:
    def __init__(self):
        # empty lists to store data:
        self.questions = []
        self.user_answers = []
        self.result = []

    def generate_ques(self, generator, topic, question_type, difficulty, ques_nos, level, api_key):
        # Resets all lists
        self.questions = []
        self.user_answers = []
        self.result = []

        try:
            # generate specified no. of questions
            generator = QuestionGenerator(api_key)
            for _ in range(ques_nos):
                
                # handle mcqs
                if question_type == "Multiple choice":
                    question = generator.generate_mcq(topic, level, difficulty.lower())
                    self.questions.append({
                        'type': 'MCQ',
                        'question': question.question,
                        'options': question.options,
                        'correct_ans': question.correct_ans
                    })
                # handle fill ups
                else:
                    question = generator.generate_fillups(topic, level, difficulty.lower())
                    self.questions.append({
                        'type': 'Fill in the blank',
                        'question': question.question,
                        'correct_ans': question.answer
                    })
        except Exception as e:
            # display error
            st.error(f"Error generating question: {e}")
            return False
        return True
    
    def attempt_quiz(self):
        # display question and collect user answer
        for i, q in enumerate(self.questions):
            # display question
            st.markdown(f"**Q. no. {i+1}: {q['question']}**")

            # radio button handling for mcq
            if q['type'] == 'MCQ':
                st.radio(
                    label=f"Select an answer for Question {i+1}",
                    options=q['options'],
                    key = f"mcq_{i}"
                )
                # self.user_answers.append(user_ans)

            #handle fill ups
            else:
                st.text_input(
                    label=f"fill in the blank for question {i+1}",
                    key = f"fill_blank_{i}"
                )
                # self.user_answers.append(user_ans)

    def evaluate_quiz(self):
        # reset results before evaluation
        self.result = []
        # evaluate each quest and user ans pair
        for i, q in enumerate(self.questions):
            # create base result dictionary
            key = f"mcq_{i}" if q['type']=='MCQ' else f"fill_blank_{i}"
            user_ans = st.session_state.get(key, "").strip()

            is_correct = False
            if q['type'] == 'MCQ':
                is_correct = (user_ans == q['correct_ans'])
            else:
                is_correct = (user_ans.lower() == q['correct_ans'].strip().lower())

            result_dict = {
                'question_no': i+1,
                'question': q['question'],
                'question_type': q['type'],
                'user_ans': user_ans,
                'correct_ans': q['correct_ans'],
                'is_correct': False
            }

            # evaluate mcq 
            if q['type'] == 'MCQ':
                result_dict['options'] = q['options']
                result_dict['is_correct'] = user_ans == q['correct_ans']

            # evaluate fill ups
            else:
                result_dict['options'] = []
                result_dict['is_correct'] = user_ans.strip().lower() == q['correct_ans'].strip().lower()

            self.result.append(result_dict)

    def generate_result_df(self):
        # convert results to pandas df
        if not self.result:
            return pd.DataFrame()
        return pd.DataFrame(self.result)
    
    def save_to_csv(self, filename = 'Quiz_results.csv'):
        try:
            # check if result exists
            if not self.result:
                st.warning("No results to save. Please complete the quiz first.")
                return None
            
            #generate df from result
            df = self.generate_result_df()

            #create unique filename with time stamp
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_filename = f"quiz_result_{timestamp}.txt"

            # ensure result directory exists
            os.makedirs('results', exist_ok=True)
            full_path = os.path.join('results', unique_filename)

            #save result to csv
            df.to_(full_path, index=False)

            # display msg
            st.success(f"Results saved to {full_path}")
            return full_path
        
        except Exception as e:
            # handle error during saving
            st.error(f"Failed to save result: {e}")
            return None
        
    def save_to_pdf(self):
        try:
            if not self.result:
                st.warning("No results to save. Please complete the quiz first.")
                return None

            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"quiz_result_{timestamp}.pdf"
            os.makedirs('results', exist_ok=True)
            full_path = os.path.join('results', filename)

            c = canvas.Canvas(full_path, pagesize=letter)
            width, height = letter
            y = height - 40
            c.setFont("Helvetica", 12)

            for res in self.result:
                lines = [
                    f"Question {res['question_no']}: {res['question']}",
                    f"Options: {', '.join(res['options'])}" if res['question_type'] == 'MCQ' else "",
                    f"Your Answer: {res['user_ans']}",
                    f"Correct Answer: {res['correct_ans']}",
                    f"Result: {'Correct' if res['is_correct'] else 'Incorrect'}",
                    "-" * 80
                ]
                for line in lines:
                    if line:
                        c.drawString(40, y, line)
                        y -= 20
                    if y < 60:
                        c.showPage()
                        c.setFont("Helvetica", 12)
                        y = height - 40

            c.save()
            st.success(f"Results saved to {full_path}")
            return full_path

        except Exception as e:
            st.error(f"Failed to save PDF: {e}")
            return None
        
def main():

    st.set_page_config(page_title="Quiz Generator",layout="wide")

    # st.sidebar.markdown("""
    # <style>
    #     .watermark {
    #         position: fixed;
    #         bottom: 15px;
    #         left: 25px;
    #         opacity: 0.6;
    #         font-size: 15px;
    #         z-index: 1000;
    #     }
    # </style>
    # <div class="watermark">Developed by <b>Lakshya Jha</b></div>
    # """, unsafe_allow_html=True)

    st.sidebar.markdown("""
    <style>
        .watermark {
            position: fixed;
            bottom: 15px;
            left: 25px;
            opacity: 0.7;
            font-size: 15px;
            z-index: 1000;
        }
        
        .icon-links{
            margin-left: 50px;
        }
                        
        .icon-links img {
            height: 20px;
            margin-right: 8px;
        }
    </style>
    <div class="watermark">
        Developed by <b>Lakshya Jha</b><br>
        <span class="icon-links">
            <a href="https://github.com/laksssshhhhya" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/25/25231.png">
            </a>
            <a href="https://www.linkedin.com/in/lakshyajha2003" target="_blank">
                <img src="https://cdn-icons-png.flaticon.com/512/174/174857.png">
            </a>
        </span>
    </div>
    """, unsafe_allow_html=True)


    #initialize session state variables
    if 'quiz_manager' not in st.session_state:
        st.session_state.quiz_manager = QuizManager()
    if 'quiz_generated' not in st.session_state:
        st.session_state.quiz_generated = False
    if 'quiz_submitted' not in st.session_state:
        st.session_state.quiz_submitted = False

    #page title
    st.title("ASKLET - Quiz Generator")

    # sidebar
    st.sidebar.header("Quiz Settings:")

    #API selection dropdown
    api_key = st.sidebar.selectbox(
        f"Select API", 
        ["GROQ1", "GROQ2", "GROQ3", "GROQ4"],
        index=0
    )

    # ques type selection
    question_type = st.sidebar.selectbox(
        f"Select Question Type",
        ["Multiple choice", "Fill in the Blank"],
        index = 0
    )

    #topic input
    topic = st.sidebar.text_input(
        f"Enter topic",
        placeholder="History, geography, etc."
    )

    #level input
    level = st.sidebar.text_input(
        f"Enter your standard",
        placeholder="B.tech, Class 2, Class 3, etc."
    )

    # difficulty level
    difficulty = st.sidebar.selectbox(
        f"Difficulty Level",
        ["Easy", "Medium", "Hard"],
        index=1
    )

    # no. of question
    num_ofQues = st.sidebar.number_input(
        f"Number of Questions",
        min_value=1,
        max_value=100,
        value=5
    )

    # generate quiz button handler
    if st.sidebar.button("Generate Quiz"):
        st.session_state.quiz_submitted = False
        generator = QuestionGenerator(api_key)
        st.session_state.quiz_generated = st.session_state.quiz_manager.generate_ques(
            generator, topic, question_type, difficulty, num_ofQues, level, api_key
        )
        st.rerun()

    # display quiz if generated 
    if st.session_state.quiz_generated and st.session_state.quiz_manager.questions:
        st.header(f"Quiz")
        st.session_state.quiz_manager.attempt_quiz()

        # submit quiz button handler
        if st.button("Submit Quiz"):
            st.session_state.quiz_manager.evaluate_quiz()
            st.session_state.quiz_submitted = True
            st.rerun()

    # display result if quiz submitted
    if st.session_state.quiz_submitted:
        st.header(f"Quiz Result:")
        results_df = st.session_state.quiz_manager.generate_result_df()

        # show result if available
        if not results_df.empty:
            #calculate/display score
            correct_count = results_df['is_correct'].sum()
            tot_ques = len(results_df)
            score_percent = (correct_count/tot_ques)*100

            st.write(f"Score: {correct_count}/{tot_ques} ({score_percent:.1f}%)")

            # display detailed result
            for _, result in results_df.iterrows():
                ques_num = result['question_no']
                if result['is_correct']:
                    st.success(f"✅ Question {ques_num}: {result['question']}")
                else:
                    st.error(f"❌ Question {ques_num}: {result['question']}")
                    st.write(f"Your answer: {result['user_ans']}")
                    st.write(f"Correct answer: {result['correct_ans']}")

                st.markdown("---")

            # save result button
            if st.button("Save Result"):
                saved_file = st.session_state.quiz_manager.save_to_pdf()
                if saved_file:
                    with open(saved_file, 'rb') as f:
                        st.download_button(
                            label="Download Result",
                            data=f.read(),
                            file_name=os.path.basename(saved_file),
                            mime='application/pdf'
                        )
        else:
            st.warning("No results available. Please complete the quiz first.")

    
    # st.markdown("""
    # <hr style="margin-top: 2em;">
    # <div style="text-align: center; color: gray; font-size: 0.9em;">
    #     Developed with ❤️ by <b>Lakshya Jha</b>
    # </div>
    # """, unsafe_allow_html=True)

# entry point
if __name__ == "__main__":
    main()
