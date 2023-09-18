import streamlit as st
from api import openai_call

def display_questions(questions):
    """Displays the list of questions in a nice format."""
    for idx, q in enumerate(questions):
        st.subheader(f"Question {idx + 1}")
        st.write(q)

def main():
    st.title("PitchPerfect :sunglasses:")

    # Input in Sidebar
    st.sidebar.header("Inputs")
    
    # Text input box
    user_text = st.sidebar.text_input("Paste your work experience from your resume.:", placeholder="Extraction from PDF coming soon.", key="work_ex")

    # Slider input
    slider_value = st.sidebar.slider("Select a value:", 0, 15)

    user_position = st.sidebar.text_input("Enter the position being interviewed for:", key="interview_position")

    user_company = st.sidebar.text_input("Enter the company being Interviewed for:", key="interview_company")

    # Dropdown select box
    dropdown_options = ["Technical", "Behavioral", "Managerial"]
    user_type_interview = st.sidebar.selectbox("Type of interview:", dropdown_options)

    # Submit button
    if st.sidebar.button("Submit", key="submit_button"):
        
        # Display the inputs when the submit button is clicked
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

        api_response = openai_call(master_prompt)
        print(api_response)

        questions = api_response["choices"][0]["message"]["content"].strip().split("\n")
        display_questions(questions)

if __name__ == "__main__":
    main()
