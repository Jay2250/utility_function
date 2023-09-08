import pyparsing as pp

# Your existing parsing code here

def format_chat_template(text):
    try:
        parsed_result = grammar.parseString(text, parseAll=True)
        formatted_template = process_parsed_result(parsed_result)
        formatted_template = ensure_ending_assistant_tag(formatted_template)
        return formatted_template
    except pp.ParseException as e:
        print(f"Parse error: {e}")
        return None

def process_parsed_result(parsed_result):
    formatted_text = ""
    assistant_segment = False
    for elem in parsed_result:
        if isinstance(elem, SavedTextNode):
            if not assistant_segment:
                formatted_text += "{{#user}}"
            formatted_text += elem.text
            if assistant_segment:
                formatted_text += "{{/assistant}}"
            else:
                formatted_text += "{{/user}}"
        elif isinstance(elem, pp.ParseResults):
            if elem.getName() == "command" and elem[0] == "{{gen":
                if assistant_segment:
                    raise ValueError("Only one {{gen ... }} command allowed in an assistant segment.")
                formatted_text += "{{#assistant}}" + process_parsed_result(elem[2:-2]) + "{{/assistant}}"
            else:
                formatted_text += process_parsed_result(elem)
        elif isinstance(elem, pp.Literal):
            formatted_text += elem
        elif isinstance(elem, pp.ParseResults):
            formatted_text += process_parsed_result(elem)
        elif isinstance(elem, str):
            formatted_text += elem

        # Toggle assistant/user segment
        if isinstance(elem, pp.ParseResults) and elem.getName() == "command" and elem[0] == "{{gen":
            assistant_segment = not assistant_segment

    return formatted_text

def ensure_ending_assistant_tag(template):
    if not template.endswith("{{/assistant}}"):
        template += "{{#assistant}}{{gen}} {{/assistant}}"
    return template

# Example usage
input_text = "Hello, {{name}}! How are you? {{gen This is an assistant response.}} Some more user text."
formatted_template = format_chat_template(input_text)

if formatted_template:
    print(formatted_template)
else:
    print("Formatting failed.")
