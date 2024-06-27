from lark import Token
from td.environments.webdev import HTML
from td.learning.tokenizer import Tokenizer
from td.samplers import ConstrainedRandomSampler

max_sequence_length = 1024


def main():

    env = HTML()
    tokenizer = Tokenizer(env.grammar)
    grammar = env.grammar
    # print(grammar._lark_parser_for_start.keys())
    # print()

    def to_feed_token(token_raw):
        token = tokenizer._token_to_index[grammar.vocabulary_map[token_raw]]
        token_str = tokenizer._index_to_token[token]
        token_name = grammar.rev_vocabulary_map[token_str]
        return Token(token_name, token_str)

    rule = "style_margin_right"
    # 'style_margin_left'
    parser = grammar._lark_parser_for_start[rule].parse_interactive(start=rule)
    parser.feed_token(to_feed_token("__ANON_3"))
    parser.feed_token(to_feed_token("COLON"))
    parser.feed_token(to_feed_token("__ANON_16"))
    accepts = parser.accepts()
    print(accepts)


if __name__ == "__main__":
    main()
