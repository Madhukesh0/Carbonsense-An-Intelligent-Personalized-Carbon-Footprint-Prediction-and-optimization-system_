from pathlib import Path
s = Path('/home/ubuntu/carbonsense-manus/client/src/pages/Home.tsx').read_text()
for token in ['route === "/forecast" &&', 'route === "/netzero" &&', 'route === "/recommendations" &&']:
    i = s.find(token)
    print(token, i)
    if i >= 0:
        print(s[i:i+2200])
