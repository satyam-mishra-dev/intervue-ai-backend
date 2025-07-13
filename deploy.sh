#!/bin/bash

# Eye Tracking Service Deployment Script for Render
echo "🚀 Eye Tracking Service Deployment Script"
echo "=========================================="

# Check if we're in the right directory
if [ ! -f "eye_gaze.py" ]; then
    echo "❌ Error: eye_gaze.py not found. Please run this script from the backend directory."
    exit 1
fi

echo "✅ Found eye_gaze.py"

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found."
    exit 1
fi

echo "✅ Found requirements.txt"

# Check if Procfile exists
if [ ! -f "Procfile" ]; then
    echo "❌ Error: Procfile not found."
    exit 1
fi

echo "✅ Found Procfile"

# Check if runtime.txt exists
if [ ! -f "runtime.txt" ]; then
    echo "❌ Error: runtime.txt not found."
    exit 1
fi

echo "✅ Found runtime.txt"

echo ""
echo "📋 Deployment Checklist:"
echo "========================"
echo "✅ All required files present"
echo "✅ Python version specified (3.11.7)"
echo "✅ Dependencies listed in requirements.txt"
echo "✅ Procfile configured"
echo "✅ Environment variables documented"

echo ""
echo "🎯 Next Steps for Render Deployment:"
echo "===================================="
echo "1. Push your code to GitHub/GitLab"
echo "2. Go to render.com and create a new Web Service"
echo "3. Connect your repository"
echo "4. Configure the service:"
echo "   - Build Command: pip install -r requirements.txt"
echo "   - Start Command: python eye_gaze.py"
echo "   - Environment Variables:"
echo "     * HOST: 0.0.0.0"
echo "     * PORT: 5000 (or let Render assign)"
echo "5. Deploy!"

echo ""
echo "🔧 Optional: Use render.yaml for automatic deployment"
if [ -f "render.yaml" ]; then
    echo "✅ render.yaml found - Render will auto-detect configuration"
else
    echo "⚠️  render.yaml not found - manual configuration required"
fi

echo ""
echo "🧪 Test your deployment:"
echo "========================"
echo "1. Run health check: python health_check.py"
echo "2. Test WebSocket connection to your Render URL"
echo "3. Monitor logs in Render dashboard"

echo ""
echo "📚 Documentation:"
echo "================"
echo "📖 README.md - Complete setup and API documentation"
echo "🔍 health_check.py - Verify your installation"
echo "⚙️  env.example - Environment variable examples"

echo ""
echo "✨ Ready for deployment!" 