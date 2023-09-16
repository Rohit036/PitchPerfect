import streamlit as st
from api import openai_call

def display_questions(questions):
    """Displays the list of questions in a nice format."""
    for idx, q in enumerate(questions):
        st.subheader(f"Question {idx + 1}")
        st.write(q)

def main():
    st.title("Mock Interview Companion :sunglasses:")

    # Text input box
    user_text = st.text_input("Paste your work experience from your resume.:", placeholder = "Extraction from PDF coming soon.", key = "work_ex")

    # Slider input
    slider_value = st.slider("Select a value:", 0, 15)

    user_position = st.text_input("Enter the position being interviewed for:", key = "interview_position")

    user_company = st.text_input("Enter the company being Interviewed for:", key = "interview_company")

    # Dropdown select box
    dropdown_options = ["Technical", "Behavioral", "Managerial"]
    user_type_interview = st.selectbox("Type of interview:", dropdown_options)
    
    # Submit button
    if st.button("Submit", key="submit_button"):
        # Display the inputs when the submit button is clicked
        # st.write(f"Your WorkEx: {user_text}")
        with st.expander("Your Profile"):
            st.write(user_text)
            st.write(f"Your experience is: {slider_value}")
            st.write(f"Position interviewing for: {user_position}")
            st.write(f"Company interviewing for: {user_company}")
            st.write(f"You want to practice for: {user_type_interview}")

        prompt_1 = "Consider I am interviewing for " + user_company + " for " + user_position + " having overall experience of " + str(slider_value) + " years"
        prompt_2 = "My work experience is " + user_text
        base_prompt = """Instructions : \n 1. Create questions based on my experience, company and position I am being interviewing for and this would be a technical interview." + \
                        \n 2. The questions should be based on the skill identified in the work experience. 
        \n 3. Ask questions on detail and specific based on candidates experience. """
        

        master_prompt = prompt_1 + "\n" + prompt_2 + "\n" + base_prompt
        # st.write(master_prompt)

        api_response = openai_call(master_prompt)
        print(api_response)

        # api_response = {
        #     "choices": [
        #         {
        #             "text": "\n\n1. How have you used Linear Regression to solve business problems?\n2. What techniques have you used to clean and prepare data for analysis?\n3. What experience do you have with Natural Language Processing (NLP) techniques?\n4. Could you explain how you developed an automated system to process Prior Authorization forms?\n5. How did you use Logistic Regression, Random Forest, and XGBoost to predict food insecurity levels?\n6. What strategies have you used to effectively communicate complex data insights to clients?\n7. How have you collaborated with cross-functional teams to identify business requirements?\n8. What challenges have you faced while developing and implementing statistical and machine learning algorithms?"
        #         }
        #     ]
        # }

        questions = api_response["choices"][0]["message"]["content"].strip().split("\n")
        display_questions(questions)
    

    # prompt_1 = "Consider I am interviewing for " + user_company + " for " + user_position + " having overall experience of " + str(slider_value) + " years"
    # prompt_2 = "My work experience is " + user_text
    # base_prompt = "Create questions based on my experience, company and position I am being interviewing for and this would be a " + user_type_interview + " interview."

    # master_prompt = prompt_1 + "\n" + prompt_2 + "\n" + base_prompt
    # st.write(master_prompt)

    # print(master_prompt)
    # print("-------")

if __name__ == "__main__":
    main()
