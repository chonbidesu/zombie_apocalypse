
# utils.py

# Handle text wrapping
def wrap_text(self, text, font, max_width):
    """Wrap the text to fit inside a given width."""
    lines = []
    words = text.split(" ")
    current_line = ""

    for word in words:
        # Check if adding the word exceeds the width
        test_line = current_line + (word if current_line == "" else " " + word)
        test_width, _ = font.size(test_line)

        if test_width <= max_width:
            current_line = test_line  # Add the word to the current line
        else:
            if current_line != "":
                lines.append(current_line)  # Append the current line if it's not empty
            current_line = word  # Start a new line with the current word

    if current_line != "":  # Append the last line if it has any content
        lines.append(current_line)

    return lines


