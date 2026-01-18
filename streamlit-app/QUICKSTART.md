# CTSR Streamlit Frontend - Quick Start Guide

## 🚀 Getting Started in 5 Minutes

### Prerequisites
- Python 3.9+ installed
- CTSR Backend API running (usually on `http://localhost:8001`)

### Step 1: Install Dependencies
```bash
cd streamlit-app
pip install -r requirements.txt
```

### Step 2: Start the Application
```bash
streamlit run app.py
```

The app opens automatically at `http://localhost:8501`

### Step 3: Configure API Connection
1. Click on **Settings** in the sidebar
2. Go to **API Configuration** tab
3. Verify/update the API URL: `http://localhost:8001`
4. Enter your email for audit tracking
5. Click **Save API Settings**

### Step 4: Explore the Application

#### 📊 Dashboard
- View key performance indicators
- See trial and system status distributions
- Check data quality metrics

#### 🏭 Vendors
- Browse vendor list
- Create new vendors
- Edit vendor details

#### 💻 Systems
- Browse system instances
- Create new systems
- Manage system details

#### 🧪 Trials
- Browse clinical trials
- Create new trials
- Assign systems to trials

#### ✅ Confirmations
- View system confirmations
- Create new confirmations
- Review and approve confirmations

#### 📊 Reports
- View system analytics
- Run compliance reports
- Export data (CSV, Excel, JSON)

## 🔧 Configuration

### Environment Variables
Create `.env` file in the streamlit-app directory:
```bash
API_BASE_URL=http://localhost:8001
STREAMLIT_CLIENT_THEME_MODE=light
```

### Streamlit Config
Create `.streamlit/config.toml` for advanced settings:
```toml
[client]
showErrorDetails = false

[server]
port = 8501
headless = false
```

## 🐳 Docker Deployment

### Run with Docker
```bash
docker build -t ctsr-streamlit .
docker run -p 8501:8501 -e API_BASE_URL=http://localhost:8001 ctsr-streamlit
```

### Run with Docker Compose
```bash
docker-compose -f docker-compose.streamlit.yml up
```

## 📋 Common Tasks

### Change API Connection
1. Go to Settings
2. Click API Configuration
3. Update the API URL
4. Save and verify

### Reset Application State
1. Go to Settings
2. Click Data Management
3. Click "Reset Session" or "Clear Cache"

### Export Data
1. Go to Reports
2. Click Export Data tab
3. Select data type and format
4. Click "Generate Export"
5. Download the file

## ⚠️ Troubleshooting

### "API: Disconnected" Error
- Verify backend API is running
- Check API URL in Settings
- Ensure firewall allows connection

### Port 8501 Already in Use
```bash
streamlit run app.py --server.port 8502
```

### Module Import Error
```bash
pip install --upgrade --force-reinstall -r requirements.txt
```

### Data Not Loading
- Clear cache in Settings
- Refresh the page
- Check API logs
- Restart the app

## 📚 Learn More

- Full documentation: See [README.md](README.md)
- API documentation: See [../IMPLEMENTATION_PLAN.md](../IMPLEMENTATION_PLAN.md)
- Backend code: See [../ctsr-api](../ctsr-api)

## 🆘 Support

For issues or questions:
1. Check the troubleshooting section above
2. Review logs in terminal where Streamlit is running
3. Check browser console (F12) for client-side errors
4. Submit issue to GitHub with:
   - Error message
   - Steps to reproduce
   - API URL and version
   - Python version
