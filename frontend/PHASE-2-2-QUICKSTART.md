# 🚀 Phase 2.2 Quick Start Guide

## Test Your LLM-Enhanced Dashboard Now!

**Phase 2.2 Frontend Integration is COMPLETE** ✅  
This guide helps you test the new LLM-powered performance insights immediately.

---

## ⚡ **Instant Testing (2 minutes)**

### 1. **Start the Backend**
```bash
# In terminal 1 - Start your LLM-enhanced backend
cd backend
source pulse_venv/bin/activate
python -m src.main

# Should see: "Server running on http://localhost:8000"
```

### 2. **Start the Frontend**
```bash
# In terminal 2 - Start the new frontend
cd frontend
npm run dev

# Should see: "Local: http://localhost:3000"
```

### 3. **Test LLM Integration**
1. Open http://localhost:3000
2. Navigate to **Performance Insights** tab
3. Click **"🚀 Analyze Performance"** for Alice Johnson
4. Watch the LLM budget monitor and evidence collection!

---

## 🧪 **What You'll See**

### **LLM Budget Monitor**
- Real-time cost tracking: `$X.XX / $15.00`
- Visual progress bar showing usage
- Budget status: Healthy/Warning/Critical
- Breakdown of embedding vs LLM costs

### **Evidence Collection**
- Mode selection: **LLM Enhanced** vs **Rule-based**
- Cost estimation: `~$0.025` for LLM mode
- Real-time progress during collection
- Step-by-step processing feedback

### **Correlation Results**
- Professional correlation cards
- Confidence scores and detection methods
- LLM semantic insights (when available)
- Export functionality for meeting prep

---

## 🎯 **Key Features to Test**

### **1. Budget Awareness**
- Try switching between LLM and rule-based modes
- Watch the cost estimation change
- See automatic fallback when budget is low

### **2. Real-time Processing**
- Click "Collect & Correlate Evidence"
- Watch the processing steps in real-time
- See the loading states and progress indicators

### **3. Professional Results**
- Review correlation cards with confidence scores
- Check LLM insights for semantic understanding
- Test the export functionality

### **4. Responsive Design**
- Test on different screen sizes
- Verify mobile responsiveness
- Check tablet layout

---

## 🔧 **Testing Different Scenarios**

### **Mock Data Available**
The system includes two mock team members:
- **Alice Johnson** (alice.johnson@example.com)
- **Bob Smith** (bob.smith@example.com)

### **Test Modes**
1. **LLM Enhanced Mode**: 
   - Uses AI for semantic understanding
   - Shows cost estimation
   - Displays LLM insights

2. **Rule-based Mode**:
   - Free pattern matching
   - Fast processing
   - Cross-platform references

### **Budget Scenarios**
- **Healthy Budget**: Normal LLM operation
- **Warning (75%+)**: Yellow alerts appear
- **Critical (90%+)**: Red alerts and warnings
- **Exhausted**: Automatic fallback to rule-based

---

## 🚀 **Integration Testing**

### **Backend Connectivity Test**
1. Go to Performance Insights tab
2. The LLM Budget Monitor should load automatically
3. If you see "Loading..." indefinitely, check backend connection

### **API Endpoints Being Tested**
- `GET /api/engine-status` - Correlation engine capabilities
- `GET /api/llm-usage` - Real-time budget tracking
- `POST /api/correlate` - LLM-enhanced correlation
- `POST /api/correlate-basic` - Rule-based correlation

### **Expected Response Times**
- **Budget Monitor**: <2 seconds
- **Engine Status**: <1 second  
- **Evidence Collection**: 10-15 seconds
- **Result Display**: <1 second

---

## 🎨 **UI Testing Checklist**

### **Visual Elements**
- [ ] LLM Budget Monitor displays correctly
- [ ] Progress bars show proper percentages
- [ ] Mode selection buttons work
- [ ] Correlation cards render properly
- [ ] Export button functions

### **Interactions**
- [ ] Tab switching (Performance ↔ Team Management)
- [ ] Mode switching (LLM ↔ Rule-based)
- [ ] Evidence collection button triggers workflow
- [ ] Back navigation works correctly
- [ ] Export downloads JSON file

### **Responsive Design**
- [ ] Desktop layout (1200px+)
- [ ] Tablet layout (768px-1199px)
- [ ] Mobile layout (<768px)
- [ ] Touch interactions work on mobile

---

## 🐛 **Troubleshooting**

### **Backend Not Connecting**
```
Error: Failed to load LLM usage data
```
**Solution**: Ensure backend is running on localhost:8000

### **Budget Monitor Not Loading**
```
Infinite "Loading LLM usage..." state
```
**Solution**: Check backend `/api/llm-usage` endpoint

### **Evidence Collection Fails**
```
"Correlation failed: [error message]"
```
**Solution**: Verify all backend APIs are operational

### **Common Issues**
1. **Port Conflicts**: Backend must be on :8000, frontend on :3000
2. **API Keys**: Backend needs valid OpenAI/Anthropic keys
3. **CORS**: Backend should allow frontend origin
4. **Dependencies**: Run `npm install` if components missing

---

## 📊 **Performance Expectations**

### **Development Mode**
- First load: ~3-5 seconds
- Subsequent loads: <1 second (cached)
- Evidence collection: 10-15 seconds
- Budget updates: Every 30 seconds

### **Production Mode**
- First load: ~1-2 seconds
- Evidence collection: 5-10 seconds
- Real-time updates: <500ms
- Export download: Instant

---

## 🎉 **Success Indicators**

### **✅ Everything Working When You See:**
1. **LLM Budget Monitor**: Shows current usage and remaining budget
2. **Mode Selection**: Can switch between LLM and rule-based
3. **Evidence Collection**: Progress steps appear during processing
4. **Results Display**: Correlations appear with confidence scores
5. **Export Function**: Downloads JSON file successfully

### **🚀 Ready for Production When:**
- All test scenarios work smoothly
- No console errors in browser
- Responsive design looks good
- Real-time updates are working
- Performance meets expectations

---

## 🔥 **Next Steps**

### **For Immediate Use**
1. Test with your team members
2. Try different correlation modes
3. Export results for actual meetings
4. Monitor LLM costs in real-time

### **For Production Deployment**
1. Replace mock data with real team API
2. Configure production API endpoints
3. Set up authentication integration
4. Monitor performance metrics

**🎯 Your LLM-enhanced performance dashboard is ready to use!** 