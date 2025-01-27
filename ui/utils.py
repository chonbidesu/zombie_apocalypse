def wrap_text(text, font, max_width):
    """Wrap text to fit within max_width."""
    lines, words, current_line = [], text.split(" "), ""
    for word in words:
        test_line = current_line + (word if not current_line else " " + word)
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines
