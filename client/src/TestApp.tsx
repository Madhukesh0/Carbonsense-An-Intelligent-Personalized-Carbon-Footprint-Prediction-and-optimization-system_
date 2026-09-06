/**
 * Minimal test component to verify React is rendering
 * 
 * To use this test:
 * 1. Open client/src/main.tsx
 * 2. Change: import App from "./App";
 *    To:     import App from "./TestApp";
 * 3. Save and refresh browser
 * 4. You should see a big white box with test text
 */

export default function TestApp() {
  return (
    <div
      style={{
        minHeight: '100vh',
        padding: '50px',
        background: '#f0f9ff',
        color: '#0f172a',
        fontFamily: 'system-ui, sans-serif',
      }}
    >
      <div
        style={{
          maxWidth: '800px',
          margin: '0 auto',
          background: 'white',
          padding: '40px',
          borderRadius: '20px',
          boxShadow: '0 10px 50px rgba(0,0,0,0.1)',
        }}
      >
        <h1 style={{ fontSize: '36px', fontWeight: 'bold', marginBottom: '20px', color: '#059669' }}>
          ✅ React is Working!
        </h1>
        
        <p style={{ fontSize: '18px', marginBottom: '10px' }}>
          If you can see this message, it means:
        </p>
        
        <ul style={{ fontSize: '16px', marginLeft: '20px', marginBottom: '30px' }}>
          <li>✅ React is rendering correctly</li>
          <li>✅ Vite is compiling your TypeScript</li>
          <li>✅ The browser is loading JavaScript</li>
          <li>✅ Port 3000 is serving the app</li>
        </ul>
        
        <div
          style={{
            background: '#fef3c7',
            border: '2px solid #f59e0b',
            borderRadius: '10px',
            padding: '20px',
            marginBottom: '30px',
          }}
        >
          <p style={{ fontWeight: 'bold', marginBottom: '10px' }}>⚠️ This is a test page</p>
          <p style={{ fontSize: '14px' }}>
            To restore the real app, change <code>import App from "./TestApp"</code> back to{' '}
            <code>import App from "./App"</code> in <code>client/src/main.tsx</code>
          </p>
        </div>
        
        <div style={{ background: '#f1f5f9', padding: '20px', borderRadius: '10px', marginBottom: '20px' }}>
          <p style={{ fontSize: '14px', marginBottom: '5px' }}>
            <strong>Current timestamp:</strong> {new Date().toISOString()}
          </p>
          <p style={{ fontSize: '14px', marginBottom: '5px' }}>
            <strong>User Agent:</strong> {navigator.userAgent.substring(0, 50)}...
          </p>
          <p style={{ fontSize: '14px' }}>
            <strong>Window size:</strong> {window.innerWidth} x {window.innerHeight}
          </p>
        </div>
        
        <button
          onClick={() => {
            fetch('/api/v1/health')
              .then(res => res.json())
              .then(data => alert('Backend health: ' + JSON.stringify(data)))
              .catch(err => alert('Backend error: ' + err.message));
          }}
          style={{
            background: '#059669',
            color: 'white',
            padding: '12px 24px',
            border: 'none',
            borderRadius: '10px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
            marginRight: '10px',
          }}
        >
          Test Backend Connection
        </button>
        
        <button
          onClick={() => window.location.reload()}
          style={{
            background: '#3b82f6',
            color: 'white',
            padding: '12px 24px',
            border: 'none',
            borderRadius: '10px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
          }}
        >
          Reload Page
        </button>
      </div>
    </div>
  );
}
