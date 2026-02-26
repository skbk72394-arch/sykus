#!/usr/bin/env python3
import sys, os

def parse_syk(filename):
    # Default values aur Raw injection support
    ui = {"title": "Sykus App", "label": "Hello", "button": "Click", "raw_web": ""}
    try:
        with open(filename, 'r') as f:
            content = f.read()
            # Simple line parsing for variables
            for line in content.split('\n'):
                if "=" in line and 'raw_web' not in line:
                    key, val = line.split("=", 1)
                    ui[key.strip()] = val.strip().strip('"\'')
            # Raw Web Injection logic (Sykus ke andar HTML/JS)
            if 'raw_web = """' in content:
                ui['raw_web'] = content.split('raw_web = """')[1].split('"""')[0]
    except Exception as e: print(f"❌ Error parsing: {e}")
    return ui

def build_web(filename):
    ui = parse_syk(filename)
    print(f"🌐 [Sykus Web] Building from '{filename}'...")
    html = f"""<!DOCTYPE html>
<html>
<head><title>{ui['title']}</title></head>
<body style="background: #121212; color: white; font-family: sans-serif; text-align: center; padding: 50px;">
    <h1 style="color: #00e5ff;">{ui['title']}</h1>
    <p style="font-size: 20px;">{ui['label']}</p>
    <button style="background: #ff0055; color: white; padding: 10px 20px; border: none; border-radius: 5px;">{ui['button']}</button>
    <hr style="margin-top: 50px; border: 0.5px solid #333;">
    <div id="raw-injection">
        {ui['raw_web']}
    </div>
</body>
</html>"""
    with open("index.html", "w") as f: f.write(html)
    print("✅ Web Build Success: index.html")

def build_apk(filename):
    ui = parse_syk(filename)
    print(f"📱 [Sykus APK] Preparing Android Source from '{filename}'...")
    kivy = f"""from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
class SykusApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical', padding=20)
        layout.add_widget(Label(text='{ui['title']}', font_size=40))
        layout.add_widget(Button(text='{ui['button']}', background_color=(1,0,0.3,1)))
        return layout
if __name__ == '__main__': SykusApp().run()"""
    with open("sykus_app.py", "w") as f: f.write(kivy)
    print("✅ APK Source Ready: sykus_app.py")

def main():
    if len(sys.argv) < 4:
        print("Sykus v5.1.1 Builder\nUsage: syk build [web|apk] [file.syk]")
        return
    
    cmd, target, filename = sys.argv[1], sys.argv[2], sys.argv[3]
    
    if cmd == "build":
        if target == "web": build_web(filename)
        elif target == "apk": build_apk(filename)
        else: print("❌ Target must be 'web' or 'apk'")

if __name__ == "__main__": main()
