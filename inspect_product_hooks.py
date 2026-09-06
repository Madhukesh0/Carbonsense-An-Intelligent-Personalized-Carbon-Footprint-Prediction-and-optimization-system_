from pathlib import Path
s = Path('/home/ubuntu/carbonsense-manus/client/src/pages/Home.tsx').read_text()
start = s.index('function ProductPage')
print('start', start)
for token in ['const history = trpc.history', 'isAuthenticated', 'if (!isAuthenticated)', 'if (route === "/about")']:
    print(token, s.find(token, start))
print(s[start:start+5000])
