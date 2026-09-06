from pathlib import Path
s = Path('/home/ubuntu/carbonsense-manus/client/src/pages/Home.tsx').read_text()
i = s.find('route === "/assistant" &&')
print(s[i:i+4200])
