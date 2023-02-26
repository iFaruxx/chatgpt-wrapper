import argparse
import sys
import termios
import tty
import os

from chatgpt_wrapper.chatgpt import ChatGPT

def getch():
    # Save the current terminal settings
    old_settings = termios.tcgetattr(sys.stdin)

    try:
        # Set the terminal to raw mode
        tty.setraw(sys.stdin.fileno())

        # Read a single character of input
        char = sys.stdin.read(1)

    finally:
        # Restore the original terminal settings
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)

    return char

def main():
    parser = argparse.ArgumentParser()
    engine = ChatGPT(headless=True, timeout=90)
    engine.new_conversation()
    contenxt_prompt_str =  "Answer the following with only the single line of linux command and without any explanation and any clarification. Code should be executable on ubuntu Linux system. If you couldn't produce any command just say \"NONE\"."
    explain_prompt_str =  "Explain the command that you have most recently provided in the previous question step by step including individual flags. If you couldn't produce any command just say \"NONE\""

    parser.add_argument(
        "params",
        nargs="*",
        help="Use 'install' for install mode, or provide a prompt for ChatGPT.",
    )

    args = parser.parse_args()
    user_query = " ".join(args.params)

    while True:
        command_response = engine.ask(f"{contenxt_prompt_str} \n {user_query}")
        if "NONE" in command_response:
            print("No command found. Would you like to (q)uit or e(x)tend the context?")
            user_resp = getch()
            if user_resp == "q":
                break
            elif user_resp == "x":
                args.params.append(input("Please enter the context to extend: "))
                continue
            else:
                print("Invalid input. Exiting...")
                break
        else:
            while True:
                # Ask user (not chatgpt) if they want to execute the command in chatgpt_response accept only (y)es/(n)o/(e)xplain/e(x)tend
                print(f"Would you like to execute (y)es/(n)o/(e)xplain/e(x)tend :\n{command_response}")
                user_resp = getch()
                if user_resp == "y":
                    print("Executing...")
                    # Execute command in terminal and print the response then exit with code 0
                    print(os.system(f"{command_response}"))
                    exit(0)
                elif user_resp == "n":
                    print("Skipping...")
                    exit(0)
                elif user_resp == "e":
                    print("Explain...")
                    explanation_response = engine.ask(f"{explain_prompt_str} \n {command_response}")
                    print(explanation_response)
                elif user_resp == "x":
                    print("Extend...")
                    user_query += " " + input("Please enter the context to extend: ")
                    break

if __name__ == "__main__":
    main()
