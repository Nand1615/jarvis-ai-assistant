from core import actions

def route(intent: str, text: str = ""):


    if intent == "greeting":
        return actions.greet()

    elif intent == "time":
        return actions.get_time()
    
    elif intent == "open_website":
        return actions.open_website(text)
    
    elif intent == "open_again":
      return actions.open_again()

    elif intent == "close_app":
       return actions.close_app_by_name(text)

    elif intent == "open_app":
       return actions.open_app(text)

    elif intent == "exit":
        actions.exit_app()

    else:
        return "Sorry, I didn’t understand that."
