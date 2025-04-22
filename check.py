import streamlit as st
import json
import google.generativeai as genai
import time
from datetime import datetime
import streamlit.components.v1 as components

# Set page configuration with expanded layout
st.set_page_config(page_title="Career Simulator", page_icon="💼", layout="wide", initial_sidebar_state="collapsed")

# Define roles and their descriptions
roles = {
    "Support Engineer": "Technical support specialist who resolves customer issues, troubleshoots technical problems, and coordinates with development teams.",
    "Front-end Developer": "Software engineer who builds user interfaces and interactive components for web applications.",
    "Data Analyst": "Professional who processes and analyzes data to derive insights and support business decisions.",
    "Project Manager": "Professional who plans, executes, and closes projects while managing scope, resources, and timelines."
}

# Role-specific simulation prompts with learning mode
role_prompts = {
    "Support Engineer": """
    You are simulating a realistic work environment for a Support Engineer, but with an educational component for someone completely new to the role. Act as both the system generating support scenarios AND various stakeholders (customers, managers, developers).
    
    Follow these rules:
    1. Create realistic support tickets with technical problems of varying complexity
    2. Require the user to classify priority (P1/Critical, P2/High, P3/Medium, P4/Low)
    3. After the user responds, ALWAYS provide:
       a) Feedback on their answer
       b) A detailed "LEARNING GUIDE" section that explains how an experienced support engineer would approach this situation
       c) Give them 2-3 options for what they might do next (with clear explanations)
    4. Present new challenges based on their decisions
    5. Track and remember their previous actions within this session
    
    Keep scenarios focused on common software issues like:
    - Authentication problems
    - Performance slowdowns
    - Integration errors
    - Data sync issues
    - UI/UX problems
    - API failures
    
    Start by introducing yourself as the simulation system, explaining that you will provide guidance for beginners, and present the first simple ticket.
    """
}

# Function to generate simulation response
def generate_simulation(role, user_input, chat_history, api_key):
    # Configure the API with the provided key
    genai.configure(api_key=api_key)
    
    # Create a conversation history for Gemini in the expected format
    gemini_history = []
    
    # Construct conversation history
    for message in chat_history:
        if message["role"] == "user":
            gemini_history.append({"role": "user", "parts": [message["content"]]})
        else:  # assistant
            gemini_history.append({"role": "model", "parts": [message["content"]]})
    
    try:
        # Create a new Gemini model instance
        model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "max_output_tokens": 1200,
                "temperature": 0.7,
            }
        )
        
        # Start a chat session
        chat = model.start_chat(history=gemini_history)
        
        # Get the system prompt ready
        system_prompt = role_prompts[role]
        
        # For the first message, include the system prompt
        if not chat_history:
            response = chat.send_message(f"{system_prompt}\n\nStart the simulation now. Format your response as an email that has just landed in the user's inbox.")
        else:
            # Check for special commands
            if user_input.startswith("[HINT]"):
                # Extract the current scenario from the last assistant message
                last_message = chat_history[-1]["content"] if chat_history else ""
                hint_prompt = f"""
                The user has requested a hint. Based on the current scenario:
                
                {last_message}
                
                Please provide a metaphorical story or analogy that would help them understand how to approach this technical problem. 
                Make it relatable to everyday life. Start with "METAPHORICAL HINT:" and then tell a brief story that explains the core concepts needed.
                Keep the metaphor simple and engaging, focusing on the problem-solving approach rather than technical details.
                """
                response = chat.send_message(hint_prompt)
            elif "I don't know how to respond" in user_input or "I'm new" in user_input or "I'm a fresher" in user_input:
                prompt = "The user is indicating they're new to this role and need guidance. Please provide detailed explanations and options for how to proceed."
                response = chat.send_message(f"{prompt}\n\nUser message: {user_input}")
            else:
                # Format responses as emails in an ongoing conversation
                email_prompt = f"""
                Based on the user's response: "{user_input}"
                
                Generate your next response as a follow-up email in the conversation. If this is from a customer, it should look like a reply email. If it's from a manager or colleague, it should look like a new email about the situation.
                
                Include realistic email headers (From, To, Subject, Time) and format it like a genuine email, but focus on the educational aspects in the content.
                """
                response = chat.send_message(f"{email_prompt}")
            
        return response.text
    except Exception as e:
        return f"Error generating response: {str(e)}"

# Function to create a virtual desktop HTML
def create_virtual_desktop(role, current_email=None, unread_count=1):
    # Get current time for display
    current_time = datetime.now().strftime("%I:%M %p")
    current_date = datetime.now().strftime("%A, %B %d, %Y")
    
    # If no current email provided, use a placeholder
    if not current_email:
        current_email = """
        <div class="email-header">
            <div class="email-subject">Welcome to Your First Day!</div>
            <div class="email-meta">
                <div>From: IT Onboarding &lt;onboarding@company.com&gt;</div>
                <div>Just now</div>
            </div>
            <div class="email-meta">
                <div>To: You &lt;you@company.com&gt;</div>
            </div>
        </div>
        <div class="email-body">
            <p>Welcome to your first day as a Support Engineer!</p>
            <p>This simulation will guide you through realistic scenarios you might encounter. Check your inbox regularly for new support tickets.</p>
            <p>Use the learning aids in the sidebar when you need help.</p>
            <p>Your first support ticket should arrive shortly. Good luck!</p>
        </div>
        """
    
    html = f"""
    <style>
        :root {{
            --desktop-bg: #1e3c72;
            --icon-hover: rgba(255, 255, 255, 0.1);
            --window-header: #2a4d8f;
            --window-bg: #f5f5f5;
            --sidebar-bg: #e5e5e5;
        }}
        
        .virtual-desktop {{
            background: linear-gradient(to right, #1e3c72, #2a5298);
            border-radius: 10px;
            height: 85vh;
            position: relative;
            overflow: hidden;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin-bottom: 20px;
        }}
        
        .desktop-icons {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 25px;
            padding: 25px;
            width: fit-content;
        }}
        
        .desktop-icon {{
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 100px;
            text-align: center;
            padding: 8px;
            border-radius: 5px;
            color: white;
            cursor: pointer;
        }}
        
        .desktop-icon:hover {{
            background-color: var(--icon-hover);
        }}
        
        .icon-img {{
            width: 50px;
            height: 50px;
            margin-bottom: 8px;
        }}
        
        .icon-text {{
            font-size: 16px;
            text-shadow: 1px 1px 2px rgba(0,0,0,0.5);
        }}
        
        .window {{
            position: absolute;
            background-color: var(--window-bg);
            border-radius: 8px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.3);
            overflow: hidden;
            top: 50px;
            left: 150px;
            width: calc(100% - 180px);
            height: calc(100% - 100px);
        }}
        
        .window-header {{
            background-color: var(--window-header);
            color: white;
            padding: 12px 18px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        
        .window-title {{
            font-size: 16px;
            font-weight: 500;
        }}
        
        .window-controls {{
            display: flex;
            gap: 12px;
        }}
        
        .window-control {{
            width: 15px;
            height: 15px;
            border-radius: 50%;
        }}
        
        .minimize {{
            background-color: #ffbd2e;
        }}
        
        .maximize {{
            background-color: #28c941;
        }}
        
        .close {{
            background-color: #ff5f57;
        }}
        
        .window-content {{
            height: calc(100% - 45px);
            display: flex;
        }}
        
        .email-sidebar {{
            width: 180px;
            background-color: var(--sidebar-bg);
            height: 100%;
            padding: 15px 0;
            border-right: 1px solid #ddd;
        }}
        
        .sidebar-item {{
            padding: 12px 18px;
            cursor: pointer;
            font-size: 16px;
        }}
        
        .sidebar-item.active {{
            background-color: #d1d1d1;
            font-weight: bold;
        }}
        
        .email-list {{
            width: 220px;  /* Reduced width */
            height: 100%;
            overflow-y: auto;
            border-right: 1px solid #ddd;
        }}
        
        .email-item {{
            padding: 10px 12px;  /* Smaller padding */
            border-bottom: 1px solid #eee;
            cursor: pointer;
        }}
        
        .email-item.active {{
            background-color: #f0f7ff;
        }}
        
        .email-item .sender {{
            font-weight: bold;
            font-size: 13px;  /* Smaller font */
            margin-bottom: 4px;
        }}
        
        .email-item .subject {{
            font-size: 12px;  /* Smaller font */
            margin-bottom: 4px;
        }}
        
        .email-item .preview {{
            font-size: 11px;  /* Smaller font */
            color: #666;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        
        .email-item .time {{
            font-size: 10px;  /* Smaller font */
            color: #999;
            margin-top: 4px;
        }}
        
        .email-content {{
            flex: 1;
            display: flex;
            flex-direction: column;
            height: 100%;
            overflow: hidden;
        }}
        
        .email-toolbar {{
            padding: 10px;
            border-bottom: 1px solid #ddd;
            display: flex;
            gap: 10px;
        }}
        
        .email-toolbar-button {{
            padding: 8px 15px;
            background-color: #f0f0f0;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .email-toolbar-button:hover {{
            background-color: #e0e0e0;
        }}
        
        .email-display {{
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            font-size: 16px;
        }}
        
        .email-composer {{
            display: none;
            flex: 1;
            padding: 25px;
            overflow-y: auto;
            font-size: 16px;
            background-color: #fcfcfc;
        }}
        
        .compose-header {{
            margin-bottom: 20px;
        }}
        
        .compose-header input {{
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
            font-size: 15px;
        }}
        
        .compose-body {{
            border: 1px solid #ddd;
            border-radius: 4px;
            padding: 10px;
            height: calc(100% - 170px);
            overflow-y: auto;
        }}
        
        .compose-body textarea {{
            width: 100%;
            height: 100%;
            border: none;
            resize: none;
            font-size: 15px;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }}
        
        .compose-actions {{
            margin-top: 15px;
            display: flex;
            justify-content: space-between;
        }}
        
        .compose-button {{
            padding: 8px 15px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 14px;
        }}
        
        .send-button {{
            background-color: #0078d4;
            color: white;
        }}
        
        .cancel-button {{
            background-color: #f0f0f0;
        }}
        
        .help-button {{
            background-color: #f0ad4e;
            color: white;
        }}
        
        .email-header {{
            padding-bottom: 20px;
            border-bottom: 1px solid #eee;
            margin-bottom: 20px;
        }}
        
        .email-subject {{
            font-size: 22px;
            font-weight: bold;
            margin-bottom: 15px;
        }}
        
        .email-meta {{
            margin-bottom: 8px;
            font-size: 15px;
        }}
        
        .email-body {{
            font-size: 16px;
            line-height: 1.6;
        }}
        
        .email-body p {{
            margin-bottom: 16px;
        }}
        
        .email-body ul {{
            margin-left: 20px;
            margin-bottom: 16px;
        }}
        
        .email-body li {{
            margin-bottom: 8px;
        }}
        
        .taskbar {{
            position: absolute;
            bottom: 0;
            left: 0;
            width: 100%;
            height: 40px;
            background-color: #0a1e42;
            display: flex;
            align-items: center;
            padding: 0 20px;
            color: white;
            font-size: 14px;
        }}
        
        .start-button {{
            background-color: #2a5298;
            color: white;
            border: none;
            padding: 5px 15px;
            border-radius: 3px;
            margin-right: 20px;
            font-size: 14px;
        }}
        
        .taskbar-time {{
            position: absolute;
            right: 20px;
        }}
        
        .email-badge {{
            background-color: #ff4c4c;
            color: white;
            border-radius: 50%;
            width: 20px;
            height: 20px;
            font-size: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            position: absolute;
            top: -5px;
            right: -5px;
        }}
        
        /* Modal dialog for help options */
        .modal {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        
        .modal-content {{
            background-color: white;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 5px 25px rgba(0, 0, 0, 0.3);
            width: 500px;
            max-width: 80%;
        }}
        
        .modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }}
        
        .modal-title {{
            font-size: 20px;
            font-weight: bold;
        }}
        
        .modal-close {{
            background: none;
            border: none;
            font-size: 20px;
            cursor: pointer;
        }}
        
        .modal-body {{
            margin-bottom: 20px;
        }}
        
        .help-options {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}
        
        .help-option {{
            padding: 12px;
            border-radius: 4px;
            background-color: #f5f5f5;
            cursor: pointer;
            transition: background-color 0.2s;
        }}
        
        .help-option:hover {{
            background-color: #e0e0e0;
        }}
        
        .help-icon {{
            margin-right: 10px;
        }}
        
        /* Desktop notification */
        .desktop-notification {{
            position: absolute;
            bottom: 50px;
            right: 20px;
            background-color: rgba(0, 0, 0, 0.8);
            color: white;
            padding: 15px 20px;
            border-radius: 5px;
            font-size: 16px;
            max-width: 300px;
            animation: fadeInOut 5s forwards;
            z-index: 100;
        }}
        
        @keyframes fadeInOut {{
            0% {{ opacity: 0; transform: translateY(20px); }}
            10% {{ opacity: 1; transform: translateY(0); }}
            90% {{ opacity: 1; transform: translateY(0); }}
            100% {{ opacity: 0; transform: translateY(20px); }}
        }}
    </style>
    
    <div class="virtual-desktop" id="virtual-desktop">
        <div class="desktop-icons">
            <div class="desktop-icon" id="email-icon" onclick="document.getElementById('response-area').style.display='block';">
                <div style="position: relative;">
                    <svg class="icon-img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white">
                        <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                    </svg>
                    <div class="email-badge">{unread_count}</div>
                </div>
                <div class="icon-text">Email</div>
            </div>
            
            <div class="desktop-icon">
                <svg class="icon-img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white">
                    <path d="M20 6h-4V4c0-1.1-.9-2-2-2h-4c-1.1 0-2 .9-2 2v2H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm-8 0h-4V4h4v2z"/>
                </svg>
                <div class="icon-text">Ticketing</div>
            </div>
            
            <div class="desktop-icon">
                <svg class="icon-img" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="white">
                    <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zm-5 14h-2V9h-2V7h4v10z"/>
                </svg>
                <div class="icon-text">Knowledge Base</div>
            </div>
        </div>
        
        <div class="window">
            <div class="window-header">
                <div class="window-title">{role} - Work Email</div>
                <div class="window-controls">
                    <div class="window-control minimize"></div>
                    <div class="window-control maximize"></div>
                    <div class="window-control close"></div>
                </div>
            </div>
            <div class="window-content">
                <div class="email-sidebar">
                    <div class="sidebar-item active">Inbox ({unread_count})</div>
                    <div class="sidebar-item">Sent</div>
                    <div class="sidebar-item">Drafts</div>
                    <div class="sidebar-item">Tasks</div>
                </div>
                <div class="email-list">
                    <div class="email-item active">
                        <div class="sender">Support System</div>
                        <div class="subject">New Ticket Assigned</div>
                        <div class="preview">You have a new support ticket...</div>
                        <div class="time">Just now</div>
                    </div>
                </div>
                <div class="email-content">
                    <div class="email-toolbar">
                        <button class="email-toolbar-button" onclick="showEmailDisplay()">View</button>
                        <button class="email-toolbar-button" onclick="showEmailComposer()">Reply</button>
                        <button class="email-toolbar-button" onclick="showHelpModal()">Help Options</button>
                    </div>
                    <div class="email-display" id="email-display">
                        {current_email}
                    </div>
                    <div class="email-composer" id="email-composer">
                        <div class="compose-header">
                            <input type="text" value="Re: Support Ticket #{unread_count}" disabled>
                            <input type="text" value="To: Support System <support@company.com>" disabled>
                        </div>
                        <div class="compose-body">
                            <textarea id="compose-textarea" placeholder="Type your response here..."></textarea>
                        </div>
                        <div class="compose-actions">
                            <div>
                                <button class="compose-button cancel-button" onclick="showEmailDisplay()">Cancel</button>
                            </div>
                            <div>
                                <button class="compose-button help-button" onclick="showHelpModal()">Need Help?</button>
                                <button class="compose-button send-button" onclick="sendEmail()">Send</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Help Modal -->
        <div class="modal" id="help-modal">
            <div class="modal-content">
                <div class="modal-header">
                    <div class="modal-title">Learning Aids</div>
                    <button class="modal-close" onclick="closeHelpModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div class="help-options">
                        <div class="help-option" onclick="provideHelp('hint')">
                            <span class="help-icon">💡</span> Get a Metaphorical Hint
                        </div>
                        <div class="help-option" onclick="provideHelp('dont-know')">
                            <span class="help-icon">🆘</span> I don't know what to do
                        </div>
                        <div class="help-option" onclick="provideHelp('best-practices')">
                            <span class="help-icon">📚</span> Show me best practices
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="desktop-notification" id="notification" style="display:none;">
            <strong>New Email:</strong> You have a new support ticket assigned to you.
        </div>

        <div class="taskbar">
            <button class="start-button">Start</button>
            <span>{role} Simulator</span>
            <div class="taskbar-time">{current_time} | {current_date}</div>
        </div>
    </div>

   <script>
    // Show notification after a brief delay
    setTimeout(function() {{
        document.getElementById('notification').style.display = 'block';
        // Hide after 5 seconds
        setTimeout(function() {{
            document.getElementById('notification').style.display = 'none';
        }}, 5000);
    }}, 2000);

    // Function to show email display and hide composer
    function showEmailDisplay() {{
        document.getElementById('email-display').style.display = 'block';
        document.getElementById('email-composer').style.display = 'none';
    }}
    
    // Function to show email composer and hide display
    function showEmailComposer() {{
        document.getElementById('email-display').style.display = 'none';
        document.getElementById('email-composer').style.display = 'block';
    }}
    
    // Function to show help modal
    function showHelpModal() {{
        document.getElementById('help-modal').style.display = 'flex';
    }}
    
    // Function to close help modal
    function closeHelpModal() {{
        document.getElementById('help-modal').style.display = 'none';
    }}
    
    // Function to provide help based on option selected
    function provideHelp(type) {{
        let helpText = '';
        
        if (type === 'hint') {{
            document.getElementById('compose-textarea').value = "[HINT] I need a metaphorical explanation for this problem";
        }} else if (type === 'dont-know') {{
            document.getElementById('compose-textarea').value = "I'm not sure how to handle this situation as I'm new to this role. Can you guide me through what an experienced support engineer would do here?";
        }}else if (type === 'best-practices') {{
            document.getElementById('compose-textarea').value = "Can you explain the best practices for handling this type of issue?";
        }}
        
        showEmailComposer();
        closeHelpModal();
    }}
    
    // Function to send email response
    function sendEmail() {{
        const responseText = document.getElementById('compose-textarea').value;
        
        if (responseText) {{
            window.parent.postMessage({
                type: 'streamlit:componentValue',
                value: {{
                    email_response: responseText
                }}
            }, '*');
            
            document.getElementById('compose-textarea').value = '';
            
            showEmailDisplay();
        }}
    }}
    
    // Event listener for messages from Streamlit
    window.addEventListener('message', function(event) {{
        if (event.data.type === 'streamlit:emailUpdate') {{
            
            document.getElementById('email-display').innerHTML = event.data.content;
        }}
    }});
</script>
    """
    return html

# Function to handle messages from the virtual desktop


# Initialize session state
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'api_key_entered' not in st.session_state:
    st.session_state.api_key_entered = False
if 'learning_mode' not in st.session_state:
    st.session_state.learning_mode = True
if 'email_counter' not in st.session_state:
    st.session_state.email_counter = 1
if 'email_response' not in st.session_state:
    st.session_state.email_response = None
if 'component_value' not in st.session_state:
    st.session_state.component_value = None

# Main app layout (minimalist with focus on the virtual desktop)
st.markdown("""
<style>
    /* Hide default Streamlit elements for a cleaner look */
    .stApp header {
        display: none;
    }
    
    /* Reduce padding for more usable space */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }
    
    /* Make buttons more visible */
    .stButton>button {
        font-size: 16px;
        padding: 8px 16px;
    }
    
    /* Make text inputs larger */
    .stTextArea>div>div>textarea {
        font-size: 16px;
    }
    
    /* Hide the response area initially */
    #response-area {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# API Key input
if not st.session_state.api_key_entered:
    st.title("Career Simulator")
    st.subheader("Practice before your first day on the job!")
    
    st.write("### Enter your Google Gemini API Key")
    st.write("You can get a key from [Google AI Studio](https://makersuite.google.com/app/apikey)")
    
    api_key = st.text_input("API Key", type="password")
    if st.button("Save API Key"):
        if api_key:
            st.session_state.api_key = api_key
            st.session_state.api_key_entered = True
            st.rerun()
        else:
            st.error("Please enter a valid API key")
    
    st.stop()

# Role selection page
elif st.session_state.selected_role is None:
    st.title("Career Simulator")
    st.subheader("Select a role to begin simulation:")
    
    # Display role options in columns
    cols = st.columns(2)
    for i, (role, description) in enumerate(roles.items()):
        with cols[i % 2]:
            st.write(f"### {role}")
            st.write(description)
            if st.button(f"Start {role} Simulation", key=f"btn_{role}"):
                st.session_state.selected_role = role
                st.session_state.chat_history = []
                st.rerun()

# Simulation page
else:
    # Minimal top interface - just a small header
    st.write(f"## {st.session_state.selected_role} Virtual Workspace")
    
    # Create current email content from latest simulation response
    current_email = None
    if st.session_state.chat_history:
        latest_response = st.session_state.chat_history[-1]["content"] if st.session_state.chat_history[-1]["role"] == "assistant" else None
        if latest_response:
            current_email = f"""
            <div class="email-header">
                <div class="email-subject">Support Ticket #{st.session_state.email_counter}</div>
                <div class="email-meta">
                    <div>From: Support System &lt;support@company.com&gt;</div>
                    <div>Just now</div>
                </div>
                <div class="email-meta">
                    <div>To: You &lt;you@company.com&gt;</div>
                </div>
            </div>
            <div class="email-body">
                {latest_response.replace('\n', '<br>')}
            </div>
            """
    
    # Render virtual desktop (now much larger)
    desktop_html = create_virtual_desktop(
        st.session_state.selected_role, 
        current_email=current_email,
        unread_count=st.session_state.email_counter
    )
    component_value = components.html(desktop_html, height=700, key="virtual_desktop")

# Handle messages from the virtual desktop
if component_value:
    st.session_state.component_value = component_value
    handle_virtual_desktop_message()  # Increased height for better visibility
    
    # Response area (appears below the virtual desktop)
    st.write("### Your Response")
    
    # Initialize simulation if chat history is empty
    if len(st.session_state.chat_history) == 0:
        initial_response = generate_simulation(st.session_state.selected_role, "", [], st.session_state.api_key)
        st.session_state.chat_history.append({"role": "assistant", "content": initial_response})
        st.rerun()
    
    # User input
    if 'help_clicked' in st.session_state:
        user_input = st.session_state.help_clicked
        del st.session_state.help_clicked
    else:
        user_input = st.text_area("Compose your reply:", height=150)
        
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        send_button = st.button("Send Email", type="primary")
    with col2:
        help_button = st.button("Need Help?")
    
    # Help options
    if help_button:
        with st.expander("Learning Aids", expanded=True):
            st.write("Select an option below:")
            help_cols = st.columns(3)
            with help_cols[0]:
                if st.button("💡 Get a Metaphorical Hint"):
                    st.session_state.help_clicked = "[HINT] I need a metaphorical explanation for this problem"
                    st.rerun()
            with help_cols[1]:
                if st.button("🆘 I don't know what to do"):
                    help_response = "I'm not sure how to handle this situation as I'm new to this role. Can you guide me through what an experienced support engineer would do here?"
                    st.session_state.help_clicked = help_response
                    st.rerun()
            with help_cols[2]:
                if st.button("📚 Show me best practices"):
                    best_practices = "Can you explain the best practices for handling this type of issue?"
                    st.session_state.help_clicked = best_practices
                    st.rerun()
            
            if st.button("🔄 Start Over"):
                st.session_state.selected_role = None
                st.session_state.chat_history = []
                st.rerun()
    
    # Process user input when send button is clicked
    if send_button and user_input:
        # Add user message to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_input})
        
        # Show a spinner while generating response
        with st.spinner("Sending email and waiting for response..."):
            # Generate response
            ai_response = generate_simulation(
                st.session_state.selected_role,
                user_input,
                st.session_state.chat_history[:-1],  # Exclude the just-added user message
                st.session_state.api_key
            )
            
            # Add AI response to chat history
            st.session_state.chat_history.append({"role": "assistant", "content": ai_response})
            st.session_state.email_counter += 1
            time.sleep(1)  # Brief pause for effect
            
        st.rerun()
    
    # Collapsible history section at the bottom
    if len(st.session_state.chat_history) > 2:
        with st.expander("Previous Email Thread", expanded=False):
            for i in range(len(st.session_state.chat_history)-2):
                message = st.session_state.chat_history[i]
                if message["role"] == "assistant":
                    st.markdown(f"📥 **From: Support System**\n\n{message['content']}")
                    st.write("---")
                else:
                    st.markdown(f"📤 **Your Reply**\n\n{message['content']}")