def return_short_string(num_of_words: int, mystr: str) -> str:
    """Restricts the number of words in a string to num_of_words"""
    word_list = mystr.split()
    if len(word_list) >= num_of_words:
        return "_".join(word_list[0:num_of_words])
    else:
        return "_".join(word_list)