import rumps
import pyperclip
from openai import OpenAI
import os
import subprocess
import json
from pathlib import Path
import time
import threading

class FixAI(rumps.App):
    def __init__(self):
        super(FixAI, self).__init__("✍️")
        
        self.config_dir = Path.home() / '.fixai'
        self.config_file = self.config_dir / 'config.json'
        self.ensure_config_dir()
        
        self.config = self.load_config()
        self.api_key = self.config.get('api_key')
        if self.api_key:
            os.environ["OPENAI_API_KEY"] = self.api_key
            
        self.enhancement_modes = {
            "Professional": "Rewrite the following message to be more professional and workplace-appropriate while keeping all @mentions, links, and technical terms exactly as they are. Make it clear and concise, suitable for Slack/email business communication, but remove any casual language or unprofessional expressions. Keep professionally appropriate emojis.",
            "Friendly with Emoji": "Make this message warm and conversational with appropriate emojis! Keep the same meaning but rewrite it in a friendly, approachable tone - like chatting with a good friend. Feel free to use casual expressions and add relevant emojis to make it more engaging and fun 😊"
        }
        
        self.is_loading = False
        self.loading_timer = None
        self.loading_frames = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        self.current_frame = 0
        
        # Create menu items with updated labels
        self.enhance_professional = rumps.MenuItem("Make Professional")
        self.enhance_friendly = rumps.MenuItem("Make Friendly with Emoji")
        self.progress_indicator = rumps.MenuItem("") # Hidden by default
        
        # Simplified API key menu
        self.api_key_menu = rumps.MenuItem("Set API Key")
        
        self.menu = [
            self.enhance_professional,
            self.enhance_friendly,
            None,  # separator
            self.progress_indicator,  # Progress indicator (hidden by default)
            None,  # separator
            self.api_key_menu,
            None,  # separator
            rumps.MenuItem("About")
        ]

        # Initially hide the progress indicator
        self.progress_indicator.hide()
    
    def ensure_config_dir(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def load_config(self):
        if self.config_file.exists():
            with open(self.config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def save_config(self):
        config = {
            'api_key': self.api_key
        }
        with open(self.config_file, 'w') as f:
            json.dump(config, f)
    
    def update_loading_animation(self):
        while self.is_loading:
            self.title = self.loading_frames[self.current_frame]
            self.progress_indicator.title = f"Working... {self.loading_frames[self.current_frame]}"
            self.current_frame = (self.current_frame + 1) % len(self.loading_frames)
            time.sleep(0.1)
        self.title = "✍️"
        self.progress_indicator.hide()
    
    @rumps.clicked("About")
    def about(self, _):
        rumps.alert(
            title="Fix AI",
            message="Select text and use the menu items to improve your writing using OpenAI. \n\nMade with ❤️ by Adjie Purbojati"
        )
    
    @rumps.clicked("Set API Key")
    def set_api_key(self, _):
        window = rumps.Window(
            message='Enter your OpenAI API key:',
            title='API Key Setup',
            default_text=self.api_key or '',
            ok='Save',
            cancel='Cancel'
        )
        response = window.run()
        if response.clicked:
            self.api_key = response.text
            os.environ["OPENAI_API_KEY"] = self.api_key
            self.save_config()
            
            rumps.notification(
                title="Success",
                subtitle="API Key Saved",
                message="Your OpenAI API key has been saved"
            )
    
    def get_selected_text(self):
        try:
            script = '''
            tell application "System Events"
                keystroke "c" using command down
            end tell
            delay 0.1
            '''
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            
            if result.stderr and "not allowed assistive access" in result.stderr:
                rumps.notification(
                    title="Permission Error",
                    subtitle="Accessibility Access Required",
                    message="Please grant accessibility permission in System Preferences > Security & Privacy > Privacy > Accessibility"
                )
                # Open System Preferences to the right page
                subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])
                return None
                
            return pyperclip.paste()
        except Exception as e:
            rumps.notification(
                title="Error",
                subtitle="Failed to get selected text",
                message=str(e)
            )
            return None
    
    def paste_text(self, text):
        try:
            pyperclip.copy(text)
            script = '''
            tell application "System Events"
                keystroke "v" using command down
            end tell
            '''
            result = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
            
            if result.stderr and "not allowed assistive access" in result.stderr:
                rumps.notification(
                    title="Permission Error",
                    subtitle="Accessibility Access Required",
                    message="Please grant accessibility permission in System Preferences > Security & Privacy > Privacy > Accessibility"
                )
                subprocess.run(["open", "x-apple.systempreferences:com.apple.preference.security?Privacy_Accessibility"])
        except Exception as e:
            rumps.notification(
                title="Error",
                subtitle="Failed to paste text",
                message=str(e)
            )
    
    @rumps.clicked("Make Professional")
    def enhance_professional_text(self, _):
        self.enhance_text("Professional")
        
    @rumps.clicked("Make Friendly with Emoji")
    def enhance_friendly_text(self, _):
        self.enhance_text("Friendly with Emoji")
    
    def enhance_text(self, mode):
        if not self.api_key:
            rumps.notification(
                title="Error",
                subtitle="API Key Required",
                message="Please set your OpenAI API key first"
            )
            return
            
        original_text = self.get_selected_text()
        print(f"Selected text: {original_text}")
        
        if not original_text:
            rumps.notification(
                title="Error",
                subtitle="No Text Selected",
                message="Please select some text to enhance"
            )
            return
        
        self.is_loading = True
        self.progress_indicator.show()
        threading.Thread(target=self.update_loading_animation, daemon=True).start()
        
        try:
            client = OpenAI()
            print("OpenAI client created")
            
            prompt = self.enhancement_modes[mode]
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": f"You are a writing enhancement assistant. {prompt}"},
                    {"role": "user", "content": original_text}
                ],
                temperature=0.7
            )
            print("Got response from OpenAI")
            
            enhanced_text = response.choices[0].message.content
            self.paste_text(enhanced_text)
            
            rumps.notification(
                title="Success",
                subtitle=f"Text Enhanced ({mode})",
                message="The enhanced text has been pasted"
            )
        except Exception as e:
            print(f"Error: {str(e)}")
            rumps.notification(
                title="Error",
                subtitle="Enhancement Failed",
                message=str(e)
            )
        finally:
            self.is_loading = False

if __name__ == "__main__":
    app = FixAI()
    app.run()