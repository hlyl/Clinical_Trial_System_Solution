# CTSR Frontend Integration Testing Guide

## Overview
This guide helps verify that your CTSR Streamlit frontend is properly configured and can communicate with the backend API.

## Prerequisites
- Backend API running and accessible
- Streamlit frontend installed and running
- Basic familiarity with the web browser developer console

## Testing Checklist

### ✅ Step 1: Verify Backend is Running
```bash
# From your terminal, test the backend health endpoint
curl http://localhost:8001/health
```

Expected response:
```json
{
  "status": "healthy",
  "database": "sqlite:///./ctsr.db",
  "version": "1.0.0"
}
```

### ✅ Step 2: Start Streamlit Frontend
```bash
cd streamlit-app
streamlit run app.py
```

Look for output like:
```
  You can now view your Streamlit app in your browser.

  Local URL: http://localhost:8501
  Network URL: http://192.168.x.x:8501
```

### ✅ Step 3: Verify API Connection in UI
1. Open browser to `http://localhost:8501`
2. Look at the **System Status** section in the left sidebar
3. You should see: **✅ API: Connected**

If you see ❌ **API: Disconnected**:
- Go to Settings → API Configuration
- Verify the API Base URL is correct
- Click "Save API Settings" to test connection

### ✅ Step 4: Test Dashboard Loading
1. Click "Dashboard" in sidebar
2. Verify Key Metrics cards load (they show numbers)
3. Verify charts render (pie charts for statuses)

Expected metrics to display:
- Total Vendors
- Total Systems  
- Active Trials
- Pending Confirmations
- Validated Systems
- Failed Validations

### ✅ Step 5: Test Vendor CRUD

#### Create a Test Vendor
1. Click "Vendors" in sidebar
2. Click "Create" tab
3. Fill in form:
   - Protocol Number: `VENDOR-TEST-001`
   - Vendor Name: `Test Vendor`
   - Type: `CRO`
   - Contact: `test@example.com`
4. Click "✅ Create Vendor"
5. Verify success message appears

#### Browse Vendors
1. Click "Browse" tab
2. Verify test vendor appears in the table
3. Try filtering by vendor type

#### Manage Vendor
1. Click "Manage" tab
2. Select your test vendor from dropdown
3. Try updating the contact info
4. Click "💾 Update Vendor"
5. Verify update success message

### ✅ Step 6: Test System CRUD

#### Create a Test System
1. Click "Systems" in sidebar
2. Click "Create" tab
3. Fill in form:
   - Instance Code: `SYS-TEST-001`
   - Platform Name: `Test Platform`
   - Category: `EDC`
   - Validation Status: `PENDING`
4. Click "✅ Create System"
5. Verify success message

#### Browse Systems
1. Click "Browse" tab
2. Verify test system appears
3. Try filtering by category and validation status

#### Manage System
1. Click "Manage" tab
2. Select your test system
3. Try updating validation status to `VALIDATED`
4. Click "💾 Update System"
5. Verify update success

### ✅ Step 7: Test Trial Management

#### Create Trial
1. Click "Trials" in sidebar
2. Click "Create" tab
3. Fill form with test data
4. Click "✅ Create Trial"

#### Assign System to Trial
1. Click "Assign Systems" tab
2. Select your test trial and system
3. Set criticality to `CRITICAL`
4. Click "🔗 Link System to Trial"

### ✅ Step 8: Test Confirmations

#### Create Confirmation
1. Click "Confirmations" in sidebar
2. Click "New" tab
3. Fill in form with test data
4. Click "✅ Create Confirmation"

#### Review Confirmation
1. Click "Review" tab
2. Select pending confirmation
3. Update status to `CONFIRMED`
4. Click "🔄 Update Confirmation"

### ✅ Step 9: Test Reports

#### View Dashboard
1. Click "Reports" in sidebar
2. Click "Overview" tab
3. Verify metrics and charts load

#### Verify System Analysis
1. Click "System Analysis" tab
2. Check bar charts for system distribution

#### Test Data Export
1. Click "Export Data" tab
2. Select "All Vendors" and "CSV" format
3. Click "📥 Generate Export"
4. Click "Download CSV"
5. Verify CSV file downloads

### ✅ Step 10: Test Settings

#### API Configuration
1. Click "Settings" in sidebar
2. Click "API Configuration" tab
3. Verify current settings are displayed
4. Try changing API URL to invalid one
5. Click "Save API Settings"
6. Should show connection error
7. Revert to correct URL and save

#### Data Management
1. Click "Data Management" tab
2. Click "🗑️ Clear Cache" button
3. Verify success message
4. Reload dashboard to verify data still loads

## API Endpoint Test Matrix

| Endpoint | Method | Expected | Test Page |
|----------|--------|----------|-----------|
| `/health` | GET | 200 OK | Sidebar Status |
| `/api/v1/vendors` | GET | 200 OK | Vendors Browse |
| `/api/v1/vendors` | POST | 201 Created | Vendors Create |
| `/api/v1/systems` | GET | 200 OK | Systems Browse |
| `/api/v1/systems` | POST | 201 Created | Systems Create |
| `/api/v1/trials` | GET | 200 OK | Trials Browse |
| `/api/v1/trials` | POST | 201 Created | Trials Create |
| `/api/v1/confirmations` | GET | 200 OK | Confirmations Browse |
| `/api/v1/confirmations` | POST | 201 Created | Confirmations New |
| `/api/v1/admin/stats` | GET | 200 OK | Dashboard Metrics |

## Performance Testing

### Load Testing
Test with larger datasets:
1. Go to Vendors → Browse
2. Change "Records per page" to 100
3. Verify page loads within 5 seconds

### Response Time Check
Using browser Developer Tools (F12):
1. Open Network tab
2. Go to Dashboard
3. Most API requests should complete in < 2 seconds

### Memory Usage
Monitor browser console:
```javascript
// In browser console
console.memory.usedJSHeapSize / 1000000
```
Should be < 100 MB for normal operation

## Error Scenarios to Test

### Scenario 1: Invalid API URL
1. Settings → API Configuration
2. Change URL to `http://localhost:9999`
3. Click Save
4. Should show error message

### Scenario 2: Missing Required Fields
1. Vendors → Create
2. Leave Protocol Number empty
3. Click Create
4. Should show validation error

### Scenario 3: Network Timeout
1. Stop backend API server
2. Try to load Dashboard
3. Should show error gracefully
4. Restart API
5. Page should recover

### Scenario 4: Concurrent Operations
1. Open multiple tabs of same page
2. Create object in Tab 1
3. Refresh Tab 2
4. Should show new object

## Browser Compatibility Testing

Test in these browsers:
- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

### Testing Steps
1. Open each browser
2. Navigate to `http://localhost:8501`
3. Run through full user flow
4. Check console for JS errors (F12)
5. Verify charts render correctly
6. Test file downloads

## Automated Testing with Curl

### Test Health Endpoint
```bash
curl -i http://localhost:8001/health
```

### List Vendors
```bash
curl -i \
  -H "User-Email: test@example.com" \
  "http://localhost:8001/api/v1/vendors?limit=10"
```

### Create Vendor
```bash
curl -i -X POST \
  -H "Content-Type: application/json" \
  -H "User-Email: test@example.com" \
  -d '{
    "vendor_code": "TEST-001",
    "vendor_name": "Test Vendor",
    "vendor_type": "CRO"
  }' \
  http://localhost:8001/api/v1/vendors
```

### Get Statistics
```bash
curl -i \
  -H "User-Email: test@example.com" \
  http://localhost:8001/api/v1/admin/stats
```

## Test Data Cleanup

After testing, you may want to clean up:

### Option 1: Delete SQLite Database
```bash
# Backend directory
rm ctsr.db
```
This resets all data to empty state.

### Option 2: Reset Session State
1. Settings → Data Management
2. Click "Reset Session"

### Option 3: Clear Cache
1. Settings → Data Management
2. Click "Clear Cache"

## Troubleshooting Test Failures

### Test Fails: API Connection
- [ ] Check backend is running: `curl http://localhost:8001/health`
- [ ] Check firewall allows port 8001
- [ ] Verify API URL in Settings
- [ ] Check backend logs for errors

### Test Fails: Data Not Loading
- [ ] Check browser console for JS errors (F12)
- [ ] Check network requests (F12 → Network tab)
- [ ] Clear browser cache and reload
- [ ] Try in incognito/private mode
- [ ] Check user_email is set in Settings

### Test Fails: Forms Not Submitting
- [ ] Verify required fields are filled
- [ ] Check API URL is correct
- [ ] Look at API response in Network tab
- [ ] Check backend logs for validation errors

### Test Fails: Charts Not Rendering
- [ ] Check browser console for errors
- [ ] Verify JavaScript is enabled
- [ ] Try different browser
- [ ] Check that data is loading (view page source)

## Success Criteria

✅ All tests pass when:
- [ ] API connection status shows ✅ Connected
- [ ] All CRUD operations (Create, Read, Update) work
- [ ] Charts render without errors
- [ ] Data exports to CSV/Excel/JSON
- [ ] Settings page loads and saves correctly
- [ ] No console errors (F12)
- [ ] Page loads complete within 5 seconds
- [ ] File downloads work correctly

## Performance Benchmarks

Target response times:
- Dashboard load: < 3 seconds
- List operations: < 2 seconds  
- Create operations: < 2 seconds
- Update operations: < 2 seconds
- Report generation: < 5 seconds
- File export: < 3 seconds

## Sign-Off Checklist

- [ ] All endpoints responding
- [ ] CRUD operations working
- [ ] Charts and visualizations rendering
- [ ] Data validation working
- [ ] Error messages clear and helpful
- [ ] Performance acceptable
- [ ] No browser console errors
- [ ] Settings persisting correctly
- [ ] Responsive on different screen sizes
- [ ] Navigation working smoothly

## Next Steps

Once all tests pass:
1. Deploy to production environment
2. Configure with production API URL
3. Set up monitoring and logging
4. Train users on system
5. Monitor for issues

## Getting Help

If tests fail:
1. Check error messages in Settings
2. Review browser console (F12)
3. Check API logs
4. Verify network connectivity
5. Check documentation
6. Submit issue with test results
