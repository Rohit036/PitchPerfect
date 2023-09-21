import streamlit as st
from api import openai_call
from pypdf import PdfReader
# import PyPDF2
from io import BytesIO

def get_pdf_text(pdf_doc):
    text = ""
    pdf_reader = PdfReader(pdf_doc)
    for page in pdf_reader.pages:
        text += page.extract_text()
    return text

# def read_pdf(file):
#     """Extract text from uploaded PDF."""
#     pdf_reader = PdfReader(file)
#     all_text = ""
    
#     for page_num in range(pdf_reader.numPages):
#         page = pdf_reader.getPage(page_num)
#         all_text += page.extractText()
    
#     return all_text

def display_questions(questions):
    """Displays the list of questions in a nice format."""
    for idx, q in enumerate(questions):
        st.subheader(f"Question {idx + 1}")
        st.write(q)

def main():
    st.title("PitchPerfect :sunglasses:")
    st.header("Your Pitch. Perfected.", divider='grey') #Craft. Practice. Impress., Practice Makes Pitch Perfect.
    st.sidebar.subheader("Analyze job roles, dissect descriptions, and master tailored interview questions. Dive deep into company profiles and gear up for your perfect pitch.")
    st.sidebar.divider()
    # Input in Sidebar
    st.sidebar.subheader("Resume:")    
    user_workex_pdf = st.sidebar.file_uploader("Upload your resume here, only PDF files", type=["pdf"],accept_multiple_files=False)
    
    st.sidebar.write("OR")

    user_workex = st.sidebar.text_input("Paste your work experience from your resume:", key="user_workex")

    st.sidebar.divider()

    st.sidebar.subheader("Job Description:")
    user_jd_pdf = st.sidebar.file_uploader("Upload the job description here, only PDF files", type=["pdf"],accept_multiple_files=False)      

    st.sidebar.write("OR")

    user_jd = st.sidebar.text_input("Paste the job description from LinkedIn or anywhere:", key="user_jd")

    st.sidebar.divider()

    st.sidebar.subheader("Other Relevant Info:")
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
        if user_workex_pdf:
            user_workex_pdf_text = get_pdf_text(user_workex_pdf)
            user_workex = user_workex_pdf_text
        
        if user_jd_pdf:
            user_jd_pdf_text = get_pdf_text(user_jd_pdf)
            user_jd = user_jd_pdf_text

        work_experience_extraction_prompt = f"For the given profile which is extraction from the resume, extract the work experience/responsibilities/contributions. profile : {user_workex_pdf_text}. Put all the extracted info in nice paragraph format."
        
        extracted_work_ex = openai_call(work_experience_extraction_prompt)["choices"][0]["message"]["content"]

        key_skills_extraction_prompt = f"For the given profile which is extraction from the resume, extract the key skills/technologies. profile : {user_workex_pdf_text}. Put the extracted skills into a list."
        extracted_skill = openai_call(key_skills_extraction_prompt)["choices"][0]["message"]["content"]
        
        # Display the inputs when the submit button is clicked
        with st.expander("Your Profile"):            
            st.write(f"Your experience is: {user_num_workex}")
            st.write(f"Position interviewing for: {user_position}")
            st.write(f"Company interviewing for: {user_company}")
            st.markdown("""---""")
            st.write(f"Your Work Experience :\n {extracted_work_ex}")
            st.write(f"Your Key Skills are :\n {extracted_skill}")
            st.markdown("""---""")
            st.write(f"JD :\n {user_jd}")
        
        tab1, tab2, tab3, tab4, tab5 = st.tabs(services_options)
        
        with tab1:
            st.spinner('Creating Results')
            if "About Company" in selected_services:
                about_company_prompt = f"I am applying to {user_company} for the role of a {user_position}. I want you to provide me with key insights about the company’s vision, mission, values, any recent news and developments, and any other relevant information to prepare for my upcoming interview"
                about_company_prompt_response = openai_call(about_company_prompt)["choices"][0]["message"]["content"]
                st.write(about_company_prompt_response)
            else:
                st.write("Please select services required.")

        with tab2:
            if "Interview Questions" in selected_services: 
                st.spinner('Creating Results')             
                interview_question_prompt = f"I am applying for {user_company} at {user_company}. I have a background in {extracted_work_ex}. Here is the job description {user_jd}. Could you generate a comprehensive list of common interview questions specific to this role based on my background and the provided job description. Also create questions based on my skills too which are {extracted_skill}. Generate questions relevant to number of work experience which is {user_num_workex} in years."

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
