# Developed by dnoobnerd [https://dnoobnerd.netlify.app]    Made with Streamlit


###### Packages Used ######
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import pymysql
import os
import socket
import platform
import geocoder
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
# libraries used to parse the pdf files
import nltk
# Download NLTK data before importing pyresparser
nltk.download('stopwords', quiet=True)
nltk.download('wordnet', quiet=True)
nltk.download('punkt', quiet=True)
from pyresparser import ResumeParser
from pdfminer3.layout import LAParams, LTTextBox
from pdfminer3.pdfpage import PDFPage
from pdfminer3.pdfinterp import PDFResourceManager
from pdfminer3.pdfinterp import PDFPageInterpreter
from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
# ML Model for job field prediction
try:
    from ml_model import JobFieldPredictor
    ml_predictor = JobFieldPredictor()
    ML_MODEL_AVAILABLE = ml_predictor.is_loaded
except Exception as e:
    print(f"ML Model not available: {e}")
    ML_MODEL_AVAILABLE = False
    ml_predictor = None


###### Preprocessing functions ######


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode('utf-8')
    pdf_display = F'<iframe src="data:application/pdf;base64,{base64_pdf}" width="700" height="1000" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


###### Database Stuffs ######


# Function to initialize database connection
def init_db_connection():
    """Initialize database connection and create database if it doesn't exist"""
    # First connect without specifying database
    temp_connection = pymysql.connect(host='localhost', user='root', password='NeerajNegi@123')
    temp_cursor = temp_connection.cursor()
    
    # Create database if it doesn't exist
    temp_cursor.execute("CREATE DATABASE IF NOT EXISTS cv")
    temp_connection.commit()
    temp_cursor.close()
    temp_connection.close()
    
    # Now connect to the cv database
    connection = pymysql.connect(host='localhost', user='root', password='NeerajNegi@123', db='cv')
    cursor = connection.cursor()
    return connection, cursor

# Initialize database connection
connection, cursor = init_db_connection()


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    insert_sql = "insert into " + DB_table_name + """
    values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    insertfeed_sql = "insert into " + DBf_table_name + """
    values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()


###### Setting Page Configuration (favicon, Logo, Title) ######


st.set_page_config(
   page_title="AI Resume Analyzer",
   page_icon='./Logo/recommend.png',
   layout="wide",
   initial_sidebar_state="expanded"
)


###### Load Custom CSS ######
def load_css():
    """Load custom CSS file"""
    try:
        with open('./styles.css', 'r', encoding='utf-8') as f:
            css = f.read()
            st.markdown(f'<style>{css}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("CSS file not found. Using default styles.")


###### Main function run() ######


def run():
    # Load custom CSS
    load_css()
    
    # (Logo, Heading, Sidebar etc)
    img = Image.open('./Logo/RESUM.png')
    st.image(img, width=700)
    
    # Sidebar styling
    st.sidebar.markdown("""
        <div style='padding: 1rem 0;'>
            <h2 style='color: #4A90E2; margin-bottom: 1.5rem;'>Choose Something...</h2>
        </div>
    """, unsafe_allow_html=True)
    
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("", activities)
    
    st.sidebar.markdown("---")
    link = '<div style="padding: 1rem 0; text-align: center;"><b>Built with 🤍 by <a href="https://dnoobnerd.netlify.app/" style="text-decoration: none; color: #4A90E2; font-weight: 500;">Rakshit, Rakshita, Manoj</a></b></div>' 
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.markdown('''
        <!-- site visitors -->

        <div id="sfct2xghr8ak6lfqt3kgru233378jya38dy" hidden></div>

        <noscript>
            <a href="https://www.freecounterstat.com" title="hit counter">
                <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" border="0" title="hit counter" alt="hit counter"> -->
            </a>
        </noscript>
    
        <p>Visitors <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" title="Free Counter" Alt="web counter" width="60px"  border="0" /></p>
    
    ''', unsafe_allow_html=True)

    ###### Creating Database and Table ######


    # Create the DB (already created in init_db_connection, but kept here as safety measure)
    db_sql = """CREATE DATABASE IF NOT EXISTS cv;"""
    cursor.execute(db_sql)


    # Create table user_data and user_feedback
    DB_table_name = 'user_data'
    table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                    sec_token varchar(20) NOT NULL,
                    ip_add varchar(50) NULL,
                    host_name varchar(50) NULL,
                    dev_user varchar(50) NULL,
                    os_name_ver varchar(50) NULL,
                    latlong varchar(50) NULL,
                    city varchar(50) NULL,
                    state varchar(50) NULL,
                    country varchar(50) NULL,
                    act_name varchar(50) NOT NULL,
                    act_mail varchar(50) NOT NULL,
                    act_mob varchar(20) NOT NULL,
                    Name varchar(500) NOT NULL,
                    Email_ID VARCHAR(500) NOT NULL,
                    resume_score VARCHAR(8) NOT NULL,
                    Timestamp VARCHAR(50) NOT NULL,
                    Page_no VARCHAR(5) NOT NULL,
                    Predicted_Field BLOB NOT NULL,
                    User_level BLOB NOT NULL,
                    Actual_skills BLOB NOT NULL,
                    Recommended_skills BLOB NOT NULL,
                    Recommended_courses BLOB NOT NULL,
                    pdf_name varchar(50) NOT NULL,
                    PRIMARY KEY (ID)
                    );
                """
    cursor.execute(table_sql)


    DBf_table_name = 'user_feedback'
    tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                    (ID INT NOT NULL AUTO_INCREMENT,
                        feed_name varchar(50) NOT NULL,
                        feed_email VARCHAR(50) NOT NULL,
                        feed_score VARCHAR(5) NOT NULL,
                        comments VARCHAR(100) NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        PRIMARY KEY (ID)
                    );
                """
    cursor.execute(tablef_sql)


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':
        
        # Collecting Miscellaneous Information
        act_name = st.text_input('Name*')
        act_mail = st.text_input('Mail*')
        act_mob  = st.text_input('Mobile Number*')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.getlogin()
        os_name_ver = platform.system() + " " + platform.release()
        g = geocoder.ip('me')
        latlong = g.latlng if g and g.latlng else None
        geolocator = Nominatim(user_agent="ai_resume_analyzer", timeout=10)
        city = state = country = ''

        if latlong:
            try:
                location = geolocator.reverse(latlong, language='en')
                if location and location.raw.get('address'):
                    address = location.raw['address']
                    city = address.get('city', '')
                    state = address.get('state', '')
                    country = address.get('country', '')
            except Exception:
                pass
        latlong = latlong or ('', '')


        # Upload Resume
        st.markdown('''
            <div class="custom-card fade-in">
                <h3 style='color: #4A90E2; margin-bottom: 0.5rem;'>📄 Upload Your Resume</h3>
                <p style='color: #64748B; font-size: 1rem;'>Get smart AI-powered recommendations to improve your resume</p>
            </div>
        ''', unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Hang On While We Cook Magic For You...'):
                time.sleep(4)
        
            ### saving the uploaded resume to folder
            save_image_path = './Uploaded_Resumes/'+pdf_file.name
            pdf_name = pdf_file.name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            ### parsing and extracting whole resume 
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

                ## Showing Analyzed data from (resume_data)
                st.markdown('''
                    <div class="custom-card fade-in">
                        <h2 style='color: #4A90E2; margin-bottom: 0.5rem;'>📊 Resume Analysis</h2>
                    </div>
                ''', unsafe_allow_html=True)
                st.success("👋 Hello " + resume_data['name'] + "! Let's analyze your resume.")
                st.markdown('''
                    <div class="custom-card">
                        <h3 style='color: #4A90E2; margin-bottom: 1rem;'>👀 Your Basic Information</h3>
                    </div>
                ''', unsafe_allow_html=True)
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Degree: '+str(resume_data['degree']))                    
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))

                except:
                    pass
                ## Predicting Candidate Experience Level 

                ### Trying with different possibilities
                cand_level = ''
                if resume_data['no_of_pages'] < 1:                
                    cand_level = "NA"
                    st.markdown( '''<div class="custom-card"><h4 style='color: #EF4444;'>🎓 You are at Fresher level!</h4></div>''',unsafe_allow_html=True)
                
                #### if internship then intermediate level
                elif 'INTERNSHIP' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<div class="custom-card"><h4 style='color: #50C878;'>🚀 You are at Intermediate level!</h4></div>''',unsafe_allow_html=True)
                elif 'INTERNSHIPS' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<div class="custom-card"><h4 style='color: #50C878;'>🚀 You are at Intermediate level!</h4></div>''',unsafe_allow_html=True)
                elif 'Internship' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<div class="custom-card"><h4 style='color: #50C878;'>🚀 You are at Intermediate level!</h4></div>''',unsafe_allow_html=True)
                elif 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<div class="custom-card"><h4 style='color: #50C878;'>🚀 You are at Intermediate level!</h4></div>''',unsafe_allow_html=True)
                
                #### if Work Experience/Experience then Experience level
                elif 'EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<div class="custom-card"><h4 style='color: #4A90E2;'>💼 You are at Experienced level!</h4></div>''',unsafe_allow_html=True)
                elif 'WORK EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<div class="custom-card"><h4 style='color: #4A90E2;'>💼 You are at Experienced level!</h4></div>''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<div class="custom-card"><h4 style='color: #4A90E2;'>💼 You are at Experienced level!</h4></div>''',unsafe_allow_html=True)
                elif 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<div class="custom-card"><h4 style='color: #4A90E2;'>💼 You are at Experienced level!</h4></div>''',unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<div class="custom-card"><h4 style='color: #FFB84D;'>🎓 You are at Fresher level!</h4></div>''',unsafe_allow_html=True)


                ## Skills Analyzing and Recommendation
                st.markdown('''
                    <div class="custom-card">
                        <h3 style='color: #4A90E2; margin-bottom: 1rem;'>💡 Skills Recommendation</h3>
                    </div>
                ''', unsafe_allow_html=True)
                
                ### Current Analyzed Skills
                # Ensure skills is a list
                extracted_skills = resume_data.get('skills', [])
                if not extracted_skills:
                    extracted_skills = []
                elif not isinstance(extracted_skills, list):
                    extracted_skills = [extracted_skills] if extracted_skills else []
                
                keywords = st_tags(label='### Your Current Skills',
                text='See our skills recommendation below',value=extracted_skills,key = '1  ')

                ### Skill Recommendations Starts                
                recommended_skills = []
                reco_field = ''
                rec_course = ''
                prediction_confidence = 0.0

                # Try ML Model Prediction First (if available)
                if ML_MODEL_AVAILABLE and ml_predictor:
                    try:
                        reco_field, prediction_confidence, probabilities = ml_predictor.predict_job_field(
                            resume_text, extracted_skills
                        )
                        
                        if reco_field:
                            # Get recommended skills from ML model
                            recommended_skills = ml_predictor.get_recommended_skills(reco_field)
                            
                            # Display prediction with confidence
                            confidence_percent = prediction_confidence * 100
                            field_display_names = {
                                'Data Science': 'Data Science Jobs',
                                'Web Development': 'Web Development Jobs',
                                'Android Development': 'Android App Development Jobs',
                                'IOS Development': 'IOS App Development Jobs',
                                'UI-UX Development': 'UI-UX Development Jobs',
                                'NA': 'General/Other Fields'
                            }
                            
                            display_name = field_display_names.get(reco_field, reco_field)
                            st.success(f"**🎯 ML Model Prediction: You are looking for {display_name}** (Confidence: {confidence_percent:.1f}%)")
                            
                            # Show top probabilities if available
                            if probabilities and len(probabilities) > 1:
                                sorted_probs = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:3]
                                prob_text = ", ".join([f"{field}: {prob*100:.1f}%" for field, prob in sorted_probs])
                                st.info(f"**Top Predictions:** {prob_text}")
                            
                            recommended_keywords = st_tags(
                                label='### Recommended skills for you.',
                                text='Recommended skills generated from ML Model',
                                value=recommended_skills,
                                key='ml_pred'
                            )
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job!</h5></div>''',unsafe_allow_html=True)
                            
                            # Course recommendation based on predicted field
                            if reco_field == 'Data Science':
                                rec_course = course_recommender(ds_course)
                            elif reco_field == 'Web Development':
                                rec_course = course_recommender(web_course)
                            elif reco_field == 'Android Development':
                                rec_course = course_recommender(android_course)
                            elif reco_field == 'IOS Development':
                                rec_course = course_recommender(ios_course)
                            elif reco_field == 'UI-UX Development':
                                rec_course = course_recommender(uiux_course)
                            else:
                                rec_course = "Sorry! Not Available for this Field"
                    except Exception as e:
                        print(f"ML Prediction error: {e}")
                        reco_field = None
                
                # Fallback to Keyword-Based Prediction if ML model not available or failed
                if not reco_field:
                    ### Keywords for Recommendations (Fallback)
                    ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                    web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                    android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                    ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                    uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                    n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                    
                    ### condition starts to check skills from keywords and predict field
                    # Use the extracted_skills we already processed
                    skills_list = extracted_skills if extracted_skills else []
                    
                    # Also check resume text for keywords if skills are missing
                    resume_text_lower = resume_text.lower() if resume_text else ""
                    
                    # Debug: Show what we're checking
                    if not skills_list and resume_text_lower:
                        st.info(f"💡 No skills extracted from resume. Analyzing resume text for keywords...")
                    
                    for i in skills_list:
                    
                        #### Data science recommendation
                        if i.lower() in ds_keyword:
                            reco_field = 'Data Science'
                            st.success("**🎯 Our analysis says you are looking for Data Science Jobs.**")
                            recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '2')
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job!</h5></div>''',unsafe_allow_html=True)
                            rec_course = course_recommender(ds_course)
                            break

                        #### Web development recommendation
                        elif i.lower() in web_keyword:
                            reco_field = 'Web Development'
                            st.success("**🎯 Our analysis says you are looking for Web Development Jobs **")
                            recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '3')
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job💼</h5></div>''',unsafe_allow_html=True)
                            rec_course = course_recommender(web_course)
                            break

                        #### Android App Development
                        elif i.lower() in android_keyword:
                            reco_field = 'Android Development'
                            st.success("**🎯 Our analysis says you are looking for Android App Development Jobs **")
                            recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '4')
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job💼</h5></div>''',unsafe_allow_html=True)
                            rec_course = course_recommender(android_course)
                            break

                        #### IOS App Development
                        elif i.lower() in ios_keyword:
                            reco_field = 'IOS Development'
                            st.success("**🎯 Our analysis says you are looking for IOS App Development Jobs **")
                            recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '5')
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job💼</h5></div>''',unsafe_allow_html=True)
                            rec_course = course_recommender(ios_course)
                            break

                        #### Ui-UX Recommendation
                        elif i.lower() in uiux_keyword:
                            reco_field = 'UI-UX Development'
                            st.success("**🎯 Our analysis says you are looking for UI-UX Development Jobs **")
                            recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = '6')
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job💼</h5></div>''',unsafe_allow_html=True)
                            rec_course = course_recommender(uiux_course)
                            break

                        #### For Not Any Recommendations
                        elif i.lower() in n_any:
                            reco_field = 'NA'
                            st.warning("**⚠️ Currently our tool only predicts and recommends for Data Science, Web, Android, IOS and UI/UX Development**")
                            recommended_skills = ['No Recommendations']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Currently No Recommendations',value=recommended_skills,key = '6')
                            st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>🔮 Maybe Available in Future Updates</h5></div>''',unsafe_allow_html=True)
                            rec_course = "Sorry! Not Available for this Field"
                            break
                    
                    # If no field predicted from skills, try checking resume text directly
                    if not reco_field and resume_text_lower:
                        # Check resume text for keywords
                        if any(keyword in resume_text_lower for keyword in ds_keyword):
                            reco_field = 'Data Science'
                            st.success("**🎯 Our analysis says you are looking for Data Science Jobs.**")
                            recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = 'fallback_1')
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job!</h5></div>''',unsafe_allow_html=True)
                            rec_course = course_recommender(ds_course)
                        elif any(keyword in resume_text_lower for keyword in web_keyword):
                            reco_field = 'Web Development'
                            st.success("**🎯 Our analysis says you are looking for Web Development Jobs **")
                            recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = 'fallback_2')
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job💼</h5></div>''',unsafe_allow_html=True)
                            rec_course = course_recommender(web_course)
                        elif any(keyword in resume_text_lower for keyword in android_keyword):
                            reco_field = 'Android Development'
                            st.success("**🎯 Our analysis says you are looking for Android App Development Jobs **")
                            recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = 'fallback_3')
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job💼</h5></div>''',unsafe_allow_html=True)
                            rec_course = course_recommender(android_course)
                        elif any(keyword in resume_text_lower for keyword in ios_keyword):
                            reco_field = 'IOS Development'
                            st.success("**🎯 Our analysis says you are looking for IOS App Development Jobs **")
                            recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = 'fallback_4')
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job💼</h5></div>''',unsafe_allow_html=True)
                            rec_course = course_recommender(ios_course)
                        elif any(keyword in resume_text_lower for keyword in uiux_keyword):
                            reco_field = 'UI-UX Development'
                            st.success("**🎯 Our analysis says you are looking for UI-UX Development Jobs **")
                            recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                            recommended_keywords = st_tags(label='### Recommended skills for you.',
                            text='Recommended skills generated from System',value=recommended_skills,key = 'fallback_5')
                            st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✨ Adding these skills to your resume will boost🚀 your chances of getting a Job💼</h5></div>''',unsafe_allow_html=True)
                            rec_course = course_recommender(uiux_course)
                    
                    # If still no field predicted, set default and show message
                    if not reco_field:
                        reco_field = 'NA'
                        recommended_skills = ['No Recommendations']
                        st.warning("**⚠️ Could not determine job field. Please ensure your resume contains relevant skills.**")
                        # Still show the recommended skills section even if no match
                        st.info("💡 **Tip:** Add keywords like 'Python', 'React', 'Android', 'iOS', 'UI/UX', 'Machine Learning', etc. to your resume for better recommendations.")
                        recommended_keywords = st_tags(
                            label='### Recommended skills for you.',
                            text='No specific recommendations available. Add technical skills to your resume for better recommendations.',
                            value=recommended_skills,
                            key='no_match'
                        )
                        rec_course = "Sorry! Not Available for this Field"
                
                # Ensure we always have a reco_field set
                if not reco_field:
                    reco_field = 'NA'
                if not recommended_skills:
                    recommended_skills = ['No Recommendations']


                ## Resume Scorer & Resume Writing Tips
                st.markdown('''
                    <div class="custom-card">
                        <h3 style='color: #4A90E2; margin-bottom: 1rem;'>🥂 Resume Tips & Ideas</h3>
                    </div>
                ''', unsafe_allow_html=True)
                resume_score = 0
                
                ### Predicting Whether these key points are added to the resume
                if 'Objective' or 'Summary' in resume_text:
                    resume_score = resume_score+6
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Objective/Summary</h5></div>''',unsafe_allow_html=True)                
                else:
                    st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>❌ Please add your career objective, it will give your career intention to the Recruiters.</h5></div>''',unsafe_allow_html=True)

                if 'Education' or 'School' or 'College'  in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Education Details</h5></div>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>❌ Please add Education. It will give Your Qualification level to the recruiter</h5></div>''',unsafe_allow_html=True)

                if 'EXPERIENCE' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Experience</h5></div>''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Experience</h5></div>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>❌ Please add Experience. It will help you to stand out from crowd</h5></div>''',unsafe_allow_html=True)

                if 'INTERNSHIPS'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Internships</h5></div>''',unsafe_allow_html=True)
                elif 'INTERNSHIP'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Internships</h5></div>''',unsafe_allow_html=True)
                elif 'Internships'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Internships</h5></div>''',unsafe_allow_html=True)
                elif 'Internship'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Internships</h5></div>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>❌ Please add Internships. It will help you to stand out from crowd</h5></div>''',unsafe_allow_html=True)

                if 'SKILLS'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Skills</h5></div>''',unsafe_allow_html=True)
                elif 'SKILL'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Skills</h5></div>''',unsafe_allow_html=True)
                elif 'Skills'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Skills</h5></div>''',unsafe_allow_html=True)
                elif 'Skill'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added Skills</h5></div>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>❌ Please add Skills. It will help you a lot</h5></div>''',unsafe_allow_html=True)

                if 'HOBBIES' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Hobbies</h5></div>''',unsafe_allow_html=True)
                elif 'Hobbies' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Hobbies</h5></div>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>❌ Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</h5></div>''',unsafe_allow_html=True)

                if 'INTERESTS'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Interest</h5></div>''',unsafe_allow_html=True)
                elif 'Interests'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Interest</h5></div>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>❌ Please add Interest. It will show your interest other that job.</h5></div>''',unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Achievements</h5></div>''',unsafe_allow_html=True)
                elif 'Achievements' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Achievements</h5></div>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>❌ Please add Achievements. It will show that you are capable for the required position.</h5></div>''',unsafe_allow_html=True)

                if 'CERTIFICATIONS' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Certifications</h5></div>''',unsafe_allow_html=True)
                elif 'Certifications' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Certifications</h5></div>''',unsafe_allow_html=True)
                elif 'Certification' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Certifications</h5></div>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>❌ Please add Certifications. It will show that you have done some specialization for the required position.</h5></div>''',unsafe_allow_html=True)

                if 'PROJECTS' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Projects</h5></div>''',unsafe_allow_html=True)
                elif 'PROJECT' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Projects</h5></div>''',unsafe_allow_html=True)
                elif 'Projects' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Projects</h5></div>''',unsafe_allow_html=True)
                elif 'Project' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('''<div class="custom-card"><h5 style='color: #50C878;'>✅ Awesome! You have added your Projects</h5></div>''',unsafe_allow_html=True)
                else:
                    st.markdown('''<div class="custom-card"><h5 style='color: #64748B;'>❌ Please add Projects. It will show that you have done work related the required position or not.</h5></div>''',unsafe_allow_html=True)

                st.markdown('''
                    <div class="custom-card">
                        <h3 style='color: #4A90E2; margin-bottom: 1rem;'>📝 Resume Score</h3>
                    </div>
                ''', unsafe_allow_html=True)

                ### Score Bar
                my_bar = st.progress(0)
                score = 0
                for percent_complete in range(resume_score):
                    score +=1
                    time.sleep(0.1)
                    my_bar.progress(percent_complete + 1)

                ### Score
                st.success('** Your Resume Writing Score: ' + str(score)+'**')
                st.warning("** Note: This score is calculated based on the content that you have in your Resume. **")

                # print(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)


                ### Getting Current Date and Time
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)


                ## Calling insert_data to add all the data into user_data                
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                ## Recommending Resume Writing Video
                st.markdown('''
                    <div class="custom-card">
                        <h3 style='color: #4A90E2; margin-bottom: 1rem;'>💡 Bonus: Resume Writing Tips Video</h3>
                    </div>
                ''', unsafe_allow_html=True)
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                ## Recommending Interview Preparation Video
                st.markdown('''
                    <div class="custom-card">
                        <h3 style='color: #4A90E2; margin-bottom: 1rem;'>💡 Bonus: Interview Tips Video</h3>
                    </div>
                ''', unsafe_allow_html=True)
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

                ## On Successful Result 
                st.balloons()

            else:
                st.error('Something went wrong..')                


    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
        
        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        with st.form("my_form"):
            st.write("Feedback form")            
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.balloons()    


        # query to fetch data from user feedback table
        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


        # fetching feed_score from the query and getting the unique values and total value count 
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        # plotting pie chart for user ratings
        st.subheader("**Past User Rating's**")
        fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)


        #  Fetching Comment History
        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.subheader("**User Comment's**")
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   
        st.markdown('''
            <div class="custom-card fade-in">
                <h2 style='color: #4A90E2; margin-bottom: 1rem;'>📖 About The Tool - AI RESUME ANALYZER</h2>
            </div>
        ''', unsafe_allow_html=True)

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
            <b>Admin -</b> <br/>
            For login use <b>admin</b> as username and <b>admin@resume-analyzer</b> as password.<br/>
            It will load all the required stuffs and perform analysis.
        </p><br/><br/>

     

        ''',unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        st.markdown('''
            <div class="custom-card fade-in">
                <h2 style='color: #4A90E2; margin-bottom: 0.5rem;'>🔐 Welcome to Admin Side</h2>
                <p style='color: #64748B;'>Please login to access admin features</p>
            </div>
        ''', unsafe_allow_html=True)

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Welcome Neeraj ! Total %d " % values + " User's Have Used Our Tool : )")                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**User's Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                st.subheader("**User Rating's**")
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)

                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)

                # fetching resume_score from the query and getting the unique values and total value count                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()

                # Pie chart for Resume Score
                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)

                # fetching IP_add from the query and getting the unique values and total value count 
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)

                # fetching City from the query and getting the unique values and total value count 
                labels = plot_data.City.unique()
                values = plot_data.City.value_counts()

                # Pie chart for City
                st.subheader("**Pie-Chart for City**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                labels = plot_data.State.unique()
                values = plot_data.State.value_counts()

                # Pie chart for State
                st.subheader("**Pie-Chart for State**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count 
                labels = plot_data.Country.unique()
                values = plot_data.Country.value_counts()

                # Pie chart for Country
                st.subheader("**Pie-Chart for Country**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()
