# 🔍 Frontend Debug Instructions

## The page is blank - here's how to debug:

### 1. **Open Browser Console**
Press `F12` in your browser to open Developer Tools, then click the **Console** tab.

Look for errors or the debug messages we just added:
```
[Dashboard] Auth state: { isAuthenticated: ..., loading: ..., error: ... }
[Dashboard] Rendering loading state...
[Dashboard] Rendering final state: Guest
```

### 2. **Check Network Tab**
In Developer Tools, click the **Network** tab:
- Look for a request to `/api/v1/auth/me`
- It should return `401 Unauthorized` with `{"detail":"Authentication required"}`
- This is NORMAL for non-logged-in users

### 3. **Hard Refresh**
Sometimes the browser caches old JavaScript:
- Windows: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

### 4. **Check if JavaScript is loading**
In the Network tab, filter by **JS**:
- You should see `main.tsx` or `index.js` loading
- If you see 404 errors, the Vite build is failing

### 5. **Check the HTML**
In Developer Tools, click **Elements** tab:
- Look for `<div id="root">` 
- Inside it, you should see React components
- If it's empty (`<div id="root"></div>`), React isn't mounting

### 6. **Common Issues**

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Console shows `useAuth is not defined` | Import path issue | Check if `@/_core/hooks/useAuth` exists |
| Console shows `tailwindcss` errors | CSS import issue | Restart server |
| Network tab shows 404 for main.tsx | Vite not compiling | Check terminal for Vite errors |
| Element tab shows empty root | React crash | Check console for React errors |
| Everything looks fine but blank | CSS issue | Check if styles are applied |

### 7. **Manual Test - Add Visible Content**

If nothing else works, let's verify React is working at all.

**Open:** `client/src/App.tsx` and temporarily replace the entire content with:

```tsx
export default function App() {
  return (
    <div style={{ padding: '50px', fontSize: '24px', background: 'white', color: 'black' }}>
      <h1>CarbonSense Test - If you see this, React is working!</h1>
      <p>Server running on port 3000</p>
      <p>Timestamp: {new Date().toISOString()}</p>
    </div>
  );
}
```

Save the file, hard refresh the browser, and you should see plain text.

**If you see the test message:**
✅ React is working
✅ Vite is compiling
❌ The original App.tsx has a bug

**If you still see a blank page:**
❌ React isn't mounting
❌ Check terminal for build errors
❌ Check browser console for load errors

---

## Quick Checklist

Before debugging further, confirm:

- [ ] Terminal shows: `Server running on http://localhost:3000/`
- [ ] Terminal shows: `[FastAPI] INFO: Uvicorn running on http://127.0.0.1:8015`
- [ ] Terminal shows: `[MongoDB] Connected successfully`
- [ ] No red errors in terminal
- [ ] Browser is open to `http://localhost:3000` (not 8015!)
- [ ] Browser console is open (F12)
- [ ] You've done a hard refresh (Ctrl+Shift+R)

---

## What to Report

If still blank after all checks, please report:

1. **Browser console output** (copy/paste all errors)
2. **Network tab** (any failed requests?)
3. **Terminal output** (any Vite compilation errors?)
4. **Elements tab** (what's inside `<div id="root">`?)

This will help identify the exact issue!
