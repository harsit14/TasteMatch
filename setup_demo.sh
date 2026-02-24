#!/bin/bash

# TasteMatch + Smart Fridge Integration Demo Setup
# This script sets up and runs the complete demo system

echo "🍎 TasteMatch + Smart Fridge Integration Demo"
echo "=============================================="
echo

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    exit 1
fi

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Check if installations were successful
if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies. Please check your Python environment."
    exit 1
fi

echo "✅ Dependencies installed successfully!"
echo

# Create demo script that runs both components
cat > run_demo.py << 'EOF'
import subprocess
import time
import webbrowser
import sys
import os
import signal
import threading

def run_mock_api():
    """Run the mock Samsung SmartThings API"""
    print("🔧 Starting Samsung SmartThings API simulator...")
    try:
        return subprocess.Popen([
            sys.executable, 
            'mock_smartthings_api.py'
        ], cwd=os.getcwd())
    except Exception as e:
        print(f"❌ Failed to start mock API: {e}")
        return None

def run_streamlit():
    """Run the Streamlit demo app"""
    print("🚀 Starting TasteMatch Streamlit demo...")
    try:
        return subprocess.Popen([
            sys.executable, 
            '-m', 'streamlit', 'run', 
            'tastematch_smart_fridge_demo.py',
            '--server.port=8501',
            '--server.headless=true'
        ], cwd=os.getcwd())
    except Exception as e:
        print(f"❌ Failed to start Streamlit: {e}")
        return None

def main():
    processes = []
    
    try:
        # Start mock API
        api_process = run_mock_api()
        if api_process:
            processes.append(api_process)
            print("✅ Mock API started on http://localhost:5000")
        else:
            print("❌ Could not start mock API")
            return
        
        # Wait for API to initialize
        time.sleep(3)
        
        # Start Streamlit app
        streamlit_process = run_streamlit()
        if streamlit_process:
            processes.append(streamlit_process)
            print("✅ Streamlit demo started on http://localhost:8501")
        else:
            print("❌ Could not start Streamlit demo")
            return
        
        # Wait for Streamlit to start
        time.sleep(3)
        
        print()
        print("🎉 TasteMatch + Smart Fridge Demo is running!")
        print("=" * 50)
        print("📱 Demo Interface: http://localhost:8501")
        print("🔧 Mock API Endpoints: http://localhost:5000")
        print()
        print("📋 Demo Features:")
        print("• Samsung Family Hub inventory simulation")
        print("• Health condition filtering (diabetes, hypertension)")  
        print("• TasteMatch integration with smart fridge data")
        print("• Real-time meal recommendations")
        print()
        print("Press Ctrl+C to stop the demo")
        print("=" * 50)
        
        # Try to open browser
        try:
            webbrowser.open('http://localhost:8501')
        except:
            pass
        
        # Wait for user interrupt
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n🛑 Shutting down demo...")
        
        # Terminate all processes
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"Warning: Could not cleanly terminate process: {e}")
        
        print("✅ Demo stopped successfully!")

if __name__ == "__main__":
    main()
EOF

echo "🎯 Demo setup complete!"
echo
echo "To run the complete demo:"
echo "  python run_demo.py"
echo
echo "Or run components separately:"
echo "  1. Samsung API: python mock_smartthings_api.py"
echo "  2. TasteMatch Demo: streamlit run tastematch_smart_fridge_demo.py"
echo
echo "📋 Files created:"
echo "  • mock_smartthings_api.py - Samsung SmartThings API simulator"
echo "  • tastematch_fridge_integration.py - Integration layer"
echo "  • tastematch_smart_fridge_demo.py - Streamlit demo interface"
echo "  • run_demo.py - One-click demo launcher"
echo "  • requirements.txt - Python dependencies"
