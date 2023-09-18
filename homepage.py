import streamlit as st
from api import openai_call

def display_questions(questions):
    """Displays the list of questions in a nice format."""
    for idx, q in enumerate(questions):
        st.subheader(f"Question {idx + 1}")
        st.write(q)

def main():
    st.title("PitchPerfect :sunglasses:")
    st.header("Your Pitch. Perfected.", divider='grey') #Craft. Practice. Impress., Practice Makes Pitch Perfect.
    st.sidebar.subheader("Analyze job roles, dissect descriptions, and master tailored interview questions. Dive deep into company profiles and gear up for your perfect pitch.")

    # Input in Sidebar
    st.sidebar.header("Inputs")
    
    # Text input box
    user_workex = st.sidebar.text_input("Paste your work experience from your resume:", placeholder="Extraction from PDF coming soon.", key="user_workex")
    user_jd = st.sidebar.text_input("Paste the job description you are applying to:", placeholder="Extraction from PDF coming soon.", key="user_jd")
    # Slider input
    user_num_workex = st.sidebar.slider("Enter your relevant years of experience:", 0, 15)
    user_position = st.sidebar.text_input("Enter the position being interviewed for:", key="user_position")
    user_company = st.sidebar.text_input("Enter the company being Interviewed for:", key="user_company")
    
    # Multi-select input
    services_options = [
        "About Company", #Company Name, Job Title
        "Interview Questions", # Job title, work experience, job description
        "Email Resume", # employer email, job interest, job description
        "JD Analyzer", #job description 
        "Target Role Analyzer", # job title, job description
    ]
    selected_services = st.sidebar.multiselect("Services:", services_options)    

    # Submit button
    if st.sidebar.button("Submit", key="submit_button"):
        
        # Display the inputs when the submit button is clicked
        with st.expander("Your Profile"):            
            st.write(f"Your experience is: {user_num_workex}")
            st.write(f"Position interviewing for: {user_position}")
            st.write(f"Company interviewing for: {user_company}")
            st.markdown("""---""")
            st.write(f"Your Work Experience :\n {user_workex}")
            st.markdown("""---""")
            st.write(f"JD :\n {user_jd}")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(services_options)
        
        with tab1:
            if "About Company" in selected_services:
                about_company_prompt = f"I am applying to {user_company} for the role of a {user_position}. I want you to provide me with key insights about the company’s vision, mission, values, any recent news and developments, and any other relevant information to prepare for my upcoming interview"
                about_company_prompt_response = openai_call(about_company_prompt)["choices"][0]["message"]["content"]
                st.write(about_company_prompt_response)
            else:
                st.write("Please select services required.")

        with tab2:
            if "Interview Questions" in selected_services:              
                interview_question_prompt = f"I am applying for {user_company} at {user_company}. I have a background in {user_workex}. Here is the job description {user_jd}. Could you generate a comprehensive list of common interview questions specific to this role based on my background and the provided job description?"

                interview_question_prompt_response = openai_call(interview_question_prompt)["choices"][0]["message"]["content"].strip().split("\n")

                # api_response = api_response["choices"][0]["message"]["content"].strip().split("\n")
                display_questions(interview_question_prompt_response)
            else:
                st.write("Please select services required.")

        with tab3:
            if "Email Resume" in selected_services:
                email_resume_prompt = f"Acting as a career advisor, write an email to send a resume to an employer. The email needs to introduce me, talk about my skills, show interest in the job tile as {user_position}, and nicely ask the employer to consider them. The email should be professional but also interesting to the employer. Write the email content considering the given job description and keep email short: {user_jd}"
                email_resume_prompt_response = openai_call(email_resume_prompt)["choices"][0]["message"]["content"]
                st.write(email_resume_prompt_response)
            else:
                st.write("Please select services required.")
        
        with tab4:
            if "JD Analyzer" in selected_services:
                jd_analyzer_prompt = f"Act like a career coach, Go through the given job description carefully and figure out the main duties, important skills, and needed qualifications. And tell me what objective I should write about and which important skills I should mention in the resume. My job description is: {user_jd}"
                jd_analyzer_prompt_response = openai_call(jd_analyzer_prompt)["choices"][0]["message"]["content"]
                st.write(jd_analyzer_prompt_response)
            else:
                st.write("Please select services required.")
        
        with tab5:
            if "Target Role Analyzer" in selected_services:
                target_role_analyzer_prompt = f"What are the key skills, qualifications, and experiences that the company is seeking in the candidate for {user_position} role, and explain why?  Here is the job description of the role I am applying for {user_jd}"
                target_role_analyzer_prompt_response = openai_call(target_role_analyzer_prompt)["choices"][0]["message"]["content"]
                st.write(target_role_analyzer_prompt_response)
            else:
                st.write("Please select services required.")

if __name__ == "__main__":
    main()
