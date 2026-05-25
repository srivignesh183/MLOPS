import os
import sys
import time
from ai_model import GeminiChatSession, load_dotenv

# ANSI Escape Codes for CLI Styling
CLEAR_SCREEN = "\033[H\033[2J"
RESET = "\033[0m"
BOLD = "\033[1m"
UNDERLINE = "\033[4m"

# Foreground Colors
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"
WHITE = "\033[37m"
GRAY = "\033[90m"

# Style helpers
def color_text(text: str, color_code: str) -> str:
    return f"{color_code}{text}{RESET}"

def bold_text(text: str) -> str:
    return f"{BOLD}{text}{RESET}"

def print_banner():
    banner = f"""
{color_text("==================================================================", CYAN)}
{bold_text(color_text("         ⚡ WELCOME TO THE GEMINI INTERACTIVE TERMINAL ⚡", MAGENTA))}
{color_text("==================================================================", CYAN)}
 {bold_text("Model:")} {color_text("gemini-2.5-flash", GREEN)} (Default) | {bold_text("SDK:")} google-genai
 {bold_text("Commands:")} Type {color_text("/help", YELLOW)} to see all session controls.
{color_text("==================================================================", CYAN)}
"""
    print(banner)

def get_or_setup_api_key() -> str:
    """Loads API key or guides user to configure one."""
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    
    if api_key:
        return api_key

    print(color_text("⚠️  No Gemini API Key detected in your environment or .env file.", YELLOW))
    print("To get a free key, visit: " + color_text("https://aistudio.google.com/", CYAN))
    print()
    
    user_key = input(bold_text("Enter your Gemini API Key: ")).strip()
    if not user_key:
        print(color_text("❌ Error: API key is required to run the chat client.", RED))
        sys.exit(1)
        
    save_env = input("Would you like to save this key to a .env file for future sessions? (y/n): ").strip().lower()
    if save_env in ('y', 'yes'):
        try:
            with open(".env", "w") as f:
                f.write(f"GEMINI_API_KEY={user_key}\n")
            print(color_text("✅ Successfully saved API key to .env file!", GREEN))
        except Exception as e:
            print(color_text(f"⚠️  Could not write to .env file: {e}", YELLOW))
            
    os.environ["GEMINI_API_KEY"] = user_key
    return user_key

def print_help():
    help_text = f"""
{bold_text("Available Commands:")}
  {color_text("/help", YELLOW):<20} Display this command reference.
  {color_text("/exit", YELLOW):<20} Exit the chat session.
  {color_text("/clear", YELLOW):<20} Reset the active chat conversation history.
  {color_text("/history", YELLOW):<20} Print the complete chat history of this session.
  {color_text("/system [text]", YELLOW):<20} Set or update the dynamic system instructions / persona.
                       (Example: {color_text("/system You are a helpful code reviewer.", GRAY)})
  {color_text("/model [name]", YELLOW):<20} Change the Gemini model mid-conversation while keeping history.
                       (Example: {color_text("/model gemini-2.5-pro", GRAY)})
"""
    print(help_text)

def main():
    # Set console title
    sys.stdout.write("\x1b]2;Gemini CLI Terminal Chat\x07")
    
    print_banner()
    
    # Initialize API key and dynamic chat session
    try:
        api_key = get_or_setup_api_key()
        session = GeminiChatSession(api_key=api_key)
    except Exception as e:
        print(color_text(f"\n❌ Client Initialization Failed: {e}", RED))
        sys.exit(1)
        
    print(color_text("\n✨ Connection established! Ready to chat.", GREEN))
    print(color_text("Enter your message below. Type /exit to close the session.\n", GRAY))
    
    while True:
        try:
            user_input = input(bold_text(color_text("User ❯ ", CYAN))).strip()
            
            if not user_input:
                continue
                
            # Handle Slash Commands
            if user_input.startswith("/"):
                parts = user_input.split(" ", 1)
                cmd = parts[0].lower()
                arg = parts[1].strip() if len(parts) > 1 else ""
                
                if cmd in ("/exit", "/quit"):
                    print(color_text("\n👋 Goodbye! Session closed.", MAGENTA))
                    break
                    
                elif cmd in ("/help", "/?"):
                    print_help()
                    continue
                    
                elif cmd in ("/clear", "/reset"):
                    session.reset_chat()
                    print(color_text("\n🧹 Chat history cleared and reset to fresh state.", CYAN))
                    print()
                    continue
                    
                elif cmd == "/history":
                    history = session.get_formatted_history()
                    if not history:
                        print(color_text("\n📜 Chat history is currently empty.", YELLOW))
                    else:
                        print(color_text("\n📜 --- CHAT SESSION HISTORY ---", CYAN))
                        for turn in history:
                            role_color = CYAN if turn["role"] == "User" else MAGENTA
                            print(f"{bold_text(color_text(turn['role'], role_color))}: {turn['text']}")
                        print(color_text("📜 ----------------------------", CYAN))
                    print()
                    continue
                    
                elif cmd == "/system":
                    if not arg:
                        current_sys = session.system_instruction or "None (default helpful assistant)"
                        print(f"\n⚙️  Current System Instruction: {color_text(current_sys, YELLOW)}\n")
                    else:
                        session.update_system_instruction(arg)
                        print(color_text(f"\n⚙️  System instruction dynamically updated! (History preserved)", GREEN))
                        print(f"New system instruction: {color_text(arg, YELLOW)}\n")
                    continue
                    
                elif cmd == "/model":
                    if not arg:
                        print(f"\n🤖 Current Model: {color_text(session.model, GREEN)}")
                        print(bold_text("Standard models to choose from:"))
                        print(f"  - {color_text('gemini-2.5-flash', GREEN)} (Default - fast & smart)")
                        print(f"  - {color_text('gemini-2.5-pro', CYAN)} (Complex reasoning & coding)")
                        print(f"  - {color_text('gemini-2.0-flash', YELLOW)} (Ultra fast generation)")
                        print(f"Change model by typing: {color_text('/model <name>', YELLOW)}\n")
                    else:
                        print(color_text(f"\n🔄 Switching model to '{arg}'...", CYAN))
                        try:
                            session.change_model(arg)
                            print(color_text(f"🤖 Successfully switched to {arg}! (History preserved)\n", GREEN))
                        except Exception as switch_err:
                            print(color_text(f"❌ Failed to switch to model '{arg}': {switch_err}\n", RED))
                    continue
                    
                else:
                    print(color_text(f"\n⚠️  Unknown command '{cmd}'. Type /help to see valid commands.\n", YELLOW))
                    continue
            
            # Print response avatar
            print(f"{bold_text(color_text('Gemini ❯ ', MAGENTA))}", end="", flush=True)
            
            # Record response duration
            start_time = time.time()
            chunk_received = False
            first_chunk_time = None
            
            try:
                # Stream the output
                response_generator = session.send_message_stream(user_input)
                for chunk in response_generator:
                    if not chunk_received:
                        first_chunk_time = time.time() - start_time
                        chunk_received = True
                    print(chunk, end="", flush=True)
                
                duration = time.time() - start_time
                print() # New line after stream ends
                
                # Print micro metrics
                metrics = f"[{session.model} | Time to first token: {first_chunk_time:.2f}s | Total: {duration:.2f}s]"
                print(color_text(metrics, GRAY))
                print()
                
            except KeyboardInterrupt:
                # Allow user to cancel generation with Ctrl+C
                print(color_text("\n🛑 Response generation interrupted by user.", YELLOW))
                print()
            except Exception as api_err:
                print(color_text(f"\n❌ Error calling Gemini API: {api_err}", RED))
                print()
                
        except KeyboardInterrupt:
            # Handle Ctrl+C in the main prompt
            print(color_text("\n👋 Session interrupted. Goodbye!", MAGENTA))
            break
        except EOFError:
            # Handle Ctrl+D
            print(color_text("\n👋 Session closed. Goodbye!", MAGENTA))
            break

if __name__ == "__main__":
    main()