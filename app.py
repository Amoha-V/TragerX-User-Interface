import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time
from datetime import datetime
import random
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Set page configuration
st.set_page_config(
    page_title="TragerX Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to create a simple logo image
def create_logo_image():
    img = Image.new('RGB', (150, 150), color=(53, 106, 195))
    d = ImageDraw.Draw(img)
    d.rectangle([10, 10, 140, 140], outline=(255, 255, 255), width=3)
    d.text((30, 60), "TragerX", fill=(255, 255, 255))
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# Function to create a QR code image
def create_qr_code_image():
    img = Image.new('RGB', (200, 200), color=(255, 255, 255))
    d = ImageDraw.Draw(img)
    
    # Draw a simple QR code pattern
    square_size = 10
    for x in range(0, 20):
        for y in range(0, 20):
            if random.random() > 0.7:
                d.rectangle([x*square_size, y*square_size, 
                           (x+1)*square_size, (y+1)*square_size], 
                           fill=(0, 0, 0))
    
    # Add corner markers
    for x, y in [(0,0), (0,17), (17,0)]:
        d.rectangle([x*square_size, y*square_size, 
                   (x+3)*square_size, (y+3)*square_size], 
                   fill=(0, 0, 0))
        d.rectangle([(x+1)*square_size, (y+1)*square_size, 
                   (x+2)*square_size, (y+2)*square_size], 
                   fill=(255, 255, 255))
    
    # Add text
    d.text((40, 85), "Scan Me", fill=(0, 0, 0))
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

# Create the logo and QR code images
logo_image = create_logo_image()
qr_code_image = create_qr_code_image()

# Sidebar for navigation
st.sidebar.title("TragerX")
st.sidebar.image(logo_image, width=150)

# User type selection
user_type = st.sidebar.radio("User Type", ["Admin", "User"])

# Function to simulate trolley data
def generate_trolley_data(num_trolleys=10):
    trolleys = []
    statuses = ["Active", "Idle", "Charging", "Maintenance"]
    locations = ["Terminal A", "Terminal B", "Terminal C", "Baggage Claim", "Main Entrance"]
    
    for i in range(1, num_trolleys + 1):
        battery = random.randint(20, 100)
        status = random.choice(statuses)
        location = random.choice(locations)
        last_active = datetime.now().strftime("%H:%M:%S")
        
        trolleys.append({
            "ID": f"TX-{i:03d}",
            "Status": status,
            "Battery": battery,
            "Location": location,
            "Last Active": last_active
        })
    
    return pd.DataFrame(trolleys)

# Simulated SLAM map data
def generate_map_data(size=50):
    # Create a grid with: 
    # 0: Unknown (Black)
    # 1: Free space (Grey)
    # 2: Tentative obstacle (Yellow)
    # 3: Confirmed obstacle (Red)
    
    grid = np.ones((size, size))  # Start with all free space
    
    # Add some walls/obstacles
    for i in range(size):
        if i < 10 or i > size-10:
            grid[i, 15:20] = 3  # Confirmed obstacles
    
    # Add some tentative obstacles
    grid[25:30, 25:30] = 2
    
    # Add some unknown areas
    grid[35:45, 35:45] = 0
    
    # Current robot position
    robot_pos = (size//2, size//2)
    
    return grid, robot_pos

# Create a heatmap from grid data
def create_slam_map(grid, robot_pos):
    # Color mapping
    colors = [
        [0, 0, 0, 1],       # Black (Unknown)
        [0.8, 0.8, 0.8, 1],  # Grey (Free space)
        [1, 1, 0, 1],        # Yellow (Tentative obstacle)
        [1, 0, 0, 1]         # Red (Confirmed obstacle)
    ]
    
    colorscale = []
    for i, color in enumerate(colors):
        colorscale.append([i/3, f'rgba({int(color[0]*255)},{int(color[1]*255)},{int(color[2]*255)},{color[3]})'])
    
    fig = go.Figure(data=go.Heatmap(
        z=grid,
        colorscale=colorscale,
        showscale=False,
    ))
    
    # Add robot position
    fig.add_trace(go.Scatter(
        x=[robot_pos[1]],
        y=[robot_pos[0]],
        mode='markers',
        marker=dict(
            symbol='circle',
            color='blue',
            size=12
        ),
        name='TragerX Position'
    ))
    
    fig.update_layout(
        title="SLAM Map and Navigation",
        height=500,
        margin=dict(l=20, r=20, t=40, b=20),
        yaxis=dict(scaleanchor='x', scaleratio=1),
    )
    
    return fig

# Admin Dashboard
if user_type == "Admin":
    st.title("TragerX Admin Dashboard")
    
    # Dashboard metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(label="Active Trolleys", value=random.randint(15, 30))
    with col2:
        st.metric(label="Idle Trolleys", value=random.randint(5, 15))
    with col3:
        st.metric(label="Charging", value=random.randint(3, 10))
    with col4:
        st.metric(label="Maintenance", value=random.randint(0, 5))
    
    # Maps and trolley monitoring
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Real-time SLAM Mapping")
        grid, robot_pos = generate_map_data()
        map_fig = create_slam_map(grid, robot_pos)
        map_chart = st.plotly_chart(map_fig, use_container_width=True)
        
        # Simulate real-time updates if button is clicked
        if st.button("Simulate Movement"):
            for i in range(5):
                grid, robot_pos = generate_map_data()
                # Modify robot position to show movement
                robot_pos = (robot_pos[0] + random.randint(-3, 3), 
                             robot_pos[1] + random.randint(-3, 3))
                new_map = create_slam_map(grid, robot_pos)
                map_chart.plotly_chart(new_map, use_container_width=True)
                time.sleep(1)
    
    with col2:
        st.subheader("System Status")
        
        # Battery status chart
        battery_data = {
            'Level': ['Critical (<20%)', 'Low (20-50%)', 'Medium (50-80%)', 'High (>80%)'],
            'Count': [random.randint(0, 3), random.randint(2, 8), 
                      random.randint(5, 15), random.randint(10, 20)]
        }
        battery_df = pd.DataFrame(battery_data)
        st.bar_chart(battery_df.set_index('Level'))
        
        # System notifications
        st.subheader("Notifications")
        notifications = [
            "TragerX TX-005 battery low, routing to charging station",
            "Maintenance completed for TX-012",
            "High congestion detected in Terminal B",
            "TX-003 stuck at location [45,32], requires assistance"
        ]
        for note in notifications:
            st.info(note)
    
    # Trolley management table
    st.subheader("Trolley Fleet Management")
    trolleys_df = generate_trolley_data(15)
    
    # Add action buttons
    df_with_actions = trolleys_df.copy()
    st.dataframe(df_with_actions, use_container_width=True)
    
    # Trolley control section
    st.subheader("Trolley Control")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        selected_trolley = st.selectbox("Select Trolley", trolleys_df["ID"].tolist())
    
    with col2:
        selected_action = st.selectbox("Action", ["Send to Charging", "Recall to Base", 
                                                 "Remote Control", "Update Firmware"])
    
    with col3:
        if st.button("Execute Action"):
            st.success(f"Action '{selected_action}' executed on {selected_trolley}")

# User Interface
else:
    st.title("TragerX User Interface")
    
    # Welcome message and intro
    st.markdown("""
    ## Welcome to TragerX Smart Trolley System
    
    Your autonomous shopping and travel companion. Use this interface to request a trolley,
    track your trolley, or get assistance.
    """)
    
    # QR Code scanner simulation
    st.subheader("Scan QR Code to Connect")
    qr_col1, qr_col2 = st.columns([1, 2])
    
    with qr_col1:
        st.image(qr_code_image, width=200)
    
    with qr_col2:
        st.write("Scan the QR code with your phone camera or enter your user ID below to connect to a trolley.")
        user_id = st.text_input("User ID")
        if st.button("Connect"):
            if user_id:
                st.success(f"Connected to user account: {user_id}")
                st.session_state.connected = True
            else:
                st.error("Please enter a valid User ID")
    
    # If user is connected
    if 'connected' in st.session_state and st.session_state.connected:
        
        tab1, tab2, tab3 = st.tabs(["Request Trolley", "My Trolley", "Help"])
        
        with tab1:
            st.subheader("Request a Trolley")
            
            col1, col2 = st.columns(2)
            with col1:
                location = st.selectbox("Your Location", 
                                       ["Terminal A", "Terminal B", "Terminal C", 
                                        "Baggage Claim", "Main Entrance"])
            
            with col2:
                num_bags = st.number_input("Number of Bags", min_value=1, max_value=5, value=1)
            
            if st.button("Request Trolley"):
                st.success("Trolley TX-007 is on its way to your location!")
                st.info("Estimated arrival time: 2 minutes")
                
                # Show a progress bar
                progress_bar = st.progress(0)
                for i in range(101):
                    time.sleep(0.05)
                    progress_bar.progress(i)
                
                st.balloons()
                st.success("Your trolley has arrived! You can now use the 'My Trolley' tab to control it.")
                st.session_state.has_trolley = True
        
        with tab2:
            st.subheader("My Trolley")
            
            if 'has_trolley' in st.session_state and st.session_state.has_trolley:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### Trolley TX-007")
                    st.metric(label="Battery", value="87%")
                    st.metric(label="Status", value="Following")
                    
                    # Control buttons
                    st.write("Trolley Controls:")
                    control_col1, control_col2 = st.columns(2)
                    with control_col1:
                        if st.button("Follow Me"):
                            st.info("Trolley is now following you")
                    with control_col2:
                        if st.button("Stop"):
                            st.info("Trolley has stopped")
                    
                    if st.button("Return Trolley"):
                        st.info("Trolley will return to the nearest collection point")
                        st.session_state.has_trolley = False
                
                with col2:
                    # Simple map showing trolley location
                    st.write("Trolley Location:")
                    grid, robot_pos = generate_map_data(30)
                    map_fig = create_slam_map(grid, robot_pos)
                    st.plotly_chart(map_fig, use_container_width=True)
            else:
                st.info("You don't have an active trolley. Please request one from the 'Request Trolley' tab.")
        
        with tab3:
            st.subheader("Help & Support")
            
            st.markdown("""
            ### Frequently Asked Questions
            
            **Q: How does the autonomous trolley work?**  
            A: TragerX uses advanced SLAM technology to navigate and follow you automatically.
            
            **Q: What if my trolley gets stuck?**  
            A: Press the 'Help' button on the trolley or use the 'Request Assistance' button below.
            
            **Q: How long does the battery last?**  
            A: The trolley battery lasts approximately 8 hours on a full charge.
            """)
            
            if st.button("Request Assistance"):
                st.success("Support staff has been notified. Someone will assist you shortly.")

# Footer
st.markdown("---")
st.markdown("© 2025 TragerX Team | Sree Sai Raghav C, Sibin Paulraj S, Shakthevell M, Amoha Vivekananthan")