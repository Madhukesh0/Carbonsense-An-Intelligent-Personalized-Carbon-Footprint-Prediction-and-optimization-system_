from pathlib import Path

path = Path('/home/ubuntu/carbonsense-manus/client/src/pages/Home.tsx')
s = path.read_text()
component_start = s.index('function ProductPage')
history_start = s.index('const history = trpc.history', component_start)
state_marker = 'const [reportDetails, setReportDetails] = useState("");'
state_end = s.index(state_marker, component_start) + len(state_marker)
guards = s[state_end:history_start]
# Replace all pre-hook route returns with a simple route flag.
s = s[:state_end] + ' const isAbout = route === "/about");' + s[history_start:]
# Correct the temporary closing parenthesis from the compact source rewrite.
s = s.replace('const isAbout = route === "/about");', 'const isAbout = route === "/about";')
# Defer all original route guards until the final hook/state declaration.
current_marker = 'const [currentKg, setCurrentKg] = useState(684);'
current_end = s.index(current_marker, component_start) + len(current_marker)
s = s[:current_end] + guards + s[current_end:]
path.write_text(s)
print('Deferred ProductPage route guards until after all hooks.')
